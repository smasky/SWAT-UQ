#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <regex>
#include <memory>
// #include <format>
#include <unordered_map>
#include <sstream>
#include <filesystem>
#include <iomanip>
#include <cstdio>
#include <exception>
#include <map>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
namespace fs = std::filesystem;

struct SubEntry {
    size_t offset;      // 改存 offset 而不是 char*，方便计算，也更安全
    float original_val;
};

struct Parameter {
    int index;
    std::vector<SubEntry> entries; 
    int mode;       
    int type;       
    int precision;
    int width;     
};

// 用于流式写入的辅助结构
struct Modification {
    size_t offset;
    int width;
    char buffer[64]; // 预存格式化后的字符串
};

class SwatFileHandler {

    private:
        std::string file_content;
        std::map<int, Parameter> params;
        std::vector<size_t> line_offsets;

        void build_line_index() {
            line_offsets.clear();
            line_offsets.reserve(file_content.size() / 50); // 预估行数以减少 vector 扩容
            line_offsets.push_back(0);
    
            // 使用 find 替代手动循环，通常编译器能优化得更好
            size_t pos = 0;
            while ((pos = file_content.find('\n', pos)) != std::string::npos) {
                if (pos + 1 < file_content.size()) {
                    line_offsets.push_back(pos + 1);
                }
                pos++;
            }
        }

    public:
        SwatFileHandler(const std::string& filepath) {
            load_file(filepath);
        }
    
        void load_file(const std::string& filepath) {
            std::ifstream in(filepath, std::ios::in | std::ios::binary | std::ios::ate); // ate直接定位到末尾
            if (in) {
                size_t size = in.tellg();
                file_content.resize(size);
                in.seekg(0, std::ios::beg);
                in.read(&file_content[0], size);
                in.close();
                build_line_index(); 
            } else {
                std::cerr << "Error: Cannot open file " << filepath << std::endl;
            }
        }

        bool register_param(int index, int mode, int type, int linePos, int staPos, int endPos, int precision, int colStep = 0, int maxCols = 1) {
        
            int line_idx = linePos - 1;
            if (line_idx < 0 || line_idx >= (int)line_offsets.size()) return false;

            size_t line_start = line_offsets[line_idx];
            
            Parameter p;
            p.index = index;
            p.mode = mode;
            p.type = type;
            p.precision = precision;
            p.width = endPos - staPos + 1;
            // 预分配内存
            p.entries.reserve(maxCols);

            const char* data_ptr = file_content.data();
            size_t file_size = file_content.size();

            for (int i = 0; i < maxCols; ++i) {
                int current_shift = i * colStep;
                size_t current_offset = line_start + (staPos - 1) + current_shift;

                if (current_offset + p.width > file_size) break;

                // 优化：直接在原始 buffer 上检查换行，避免不必要的检查
                // 只要检查这段区域内有没有换行符即可
                bool hit_newline = false;
                for(int k = 0; k < p.width; ++k) {
                    char c = data_ptr[current_offset + k];
                    if (c == '\n' || c == '\r') {
                        hit_newline = true;
                        break;
                    }
                }
                if (hit_newline) break;

                // 优化：不再创建 substr，直接解析指针
                // 检查是否全为空白
                bool is_empty = true;
                for(int k = 0; k < p.width; ++k) {
                    char c = data_ptr[current_offset + k];
                    if (c != ' ' && c != '\t' && c != '\r') {
                        is_empty = false;
                        break;
                    }
                }

                if (is_empty) {
                    if (i == 0) continue; else break; 
                }

                try {
                    // 使用 std::strtof 直接从指针解析 float，避免 substr 分配内存
                    // 注意：这里假设字段是合法的数字字符串。为了安全，可以先拷贝到栈上的小 buffer
                    char temp_buf[64];
                    if (p.width < 63) {
                        std::memcpy(temp_buf, data_ptr + current_offset, p.width);
                        temp_buf[p.width] = '\0'; // 加上结束符
                        
                        char* end_ptr;
                        float val = std::strtof(temp_buf, &end_ptr);
                        
                        if (end_ptr != temp_buf) { // 成功解析
                            SubEntry entry;
                            entry.offset = current_offset; // 存 Offset
                            entry.original_val = val;            
                            p.entries.push_back(entry);
                        }
                    }
                } catch (...) {
                    break; 
                }
            }
            
            if (p.entries.empty()) return false;
            
            params[index] = p;
            return true;
        }

        /**
         * 极致优化的写入函数：
         * 1. 避免拷贝整个 file_content (Zero-Copy)
         * 2. 收集所有修改 -> 排序 -> 流式写入
         */
        void set_values_and_save(const std::string& output_filepath, 
            const std::vector<int>& indices, 
            const std::vector<double>& vals, 
            const std::vector<int>& layers) 
        {
            // 1. 收集所有需要修改的片段 (Modifications)
            std::vector<Modification> mods;
            mods.reserve(indices.size() * 5); // 预估容量

            size_t num_changes = indices.size();
            for (size_t i = 0; i < num_changes; ++i) {
                int idx = indices[i];
                if (params.find(idx) == params.end()) continue;

                const Parameter& p = params.at(idx);
                double input_val = vals[i];
                int layer_idx = layers[i];

                int start_k = 0;
                int end_k = p.entries.size();

                if (layer_idx >= 0) {
                    if (layer_idx >= (int)p.entries.size()) continue;
                    start_k = layer_idx;
                    end_k = layer_idx + 1;
                }

                for (int k = start_k; k < end_k; ++k) {
                    const SubEntry& entry = p.entries[k];
                    double final_val = 0.0;

                    if (p.mode == 0) final_val = entry.original_val * (1.0 + input_val);
                    else if (p.mode == 1) final_val = input_val;
                    else final_val = entry.original_val + input_val;

                    if (p.type == 1) final_val = (int)final_val;

                    Modification mod;
                    mod.offset = entry.offset;
                    mod.width = p.width;
                    
                    int len = std::snprintf(mod.buffer, sizeof(mod.buffer), "%*.*f", p.width, p.precision, final_val);
                    
                    if (len > p.width) {
                        std::memset(mod.buffer, '*', p.width); // 溢出处理
                    }
                    
                    mods.push_back(mod);
                }
            }

            // 2. 按 offset 排序，保证顺序写入
            std::sort(mods.begin(), mods.end(), [](const Modification& a, const Modification& b) {
                return a.offset < b.offset;
            });

            // 3. 流式写入文件 (Stream Editing)
            // 这样我们只需要读取 const 的原始数据，然后把拼凑好的数据流吐到硬盘
            std::ofstream out(output_filepath, std::ios::out | std::ios::binary);
            
            // 设置一个较大的写入缓冲区 (比如 64KB)，减少系统调用次数
            char write_buffer[65536]; 
            out.rdbuf()->pubsetbuf(write_buffer, sizeof(write_buffer));

            const char* original_data = file_content.data();
            size_t current_read_pos = 0;

            for (const auto& mod : mods) {
                // A. 写入从当前位置到下一个修改点之间的原始数据
                if (mod.offset > current_read_pos) {
                    out.write(original_data + current_read_pos, mod.offset - current_read_pos);
                }

                // B. 写入修改后的数据
                out.write(mod.buffer, mod.width);

                // C. 更新读取指针
                current_read_pos = mod.offset + mod.width;
            }

            // D. 写入剩余的所有原始数据
            if (current_read_pos < file_content.size()) {
                out.write(original_data + current_read_pos, file_content.size() - current_read_pos);
            }

            out.close();
        }
};

// name, mode, type, linePos, staPos, endPos, precision, colStep, maxCols
std::unique_ptr<SwatFileHandler> createFileHandler(
    const std::string& filepath, 
    const std::vector<int>& var_list,
    const std::vector<int>& mode_list, 
    const std::vector<int>& type_list, 
    const std::vector<int>& linePos_list, 
    const std::vector<int>& staPos_list, 
    const std::vector<int>& endPos_list, 
    const std::vector<int>& precision_list, 
    const std::vector<int>& colStep_list, 
    const std::vector<int>& maxCols_list) {

// 使用 make_unique 在堆上创建对象
auto handler = std::make_unique<SwatFileHandler>(filepath);

for (size_t i = 0; i < var_list.size(); ++i) {
    handler->register_param(var_list[i], mode_list[i], type_list[i], 
                            linePos_list[i], staPos_list[i], endPos_list[i], 
                            precision_list[i], colStep_list[i], maxCols_list[i]);
}

// 将指针所有权移交给 Python
return handler;
}


void set_value_FileHandler(SwatFileHandler& handler, 
    const std::string& file, 
    const std::vector<int>& var_list, 
    const std::vector<double>& input_values, 
    const std::vector<int>& layer_idx_list) {

handler.set_values_and_save(file, var_list, input_values, layer_idx_list);

}


std::string _generate_value(const std::string &default_value_str, const int &mode, const double &value, const int &M){
     
    double result;
    if (M == -1){
        double default_value=std::stod(default_value_str);
        if (mode==1){
            result=default_value*(1+value);
        }else if(mode==2){
            result=default_value+value;
        }else{
            result=value;
        }
        return std::to_string(result);
    }else{
        std::istringstream iss(default_value_str);
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(4);

        std::vector<double> default_values;
        
        double tmp_value;

        while (iss >> tmp_value){
            default_values.push_back(tmp_value);
        }

        for(size_t i=0; i<default_values.size(); i++){

             if (i > 0) {
                    oss << std::setw(13); // 设置间隔宽度为9（8个空格加一个字符宽度）
                }
            
            if (M!=0){

               if (M==i+1){

                if(mode==1){
                    oss << default_values[i]*(1+value);
                }else if(mode==2){
                    oss << default_values[i]+value;
                }else{
                    oss << value;
                }

                }else{
                    oss << default_values[i];
                }

            }else{

                if(mode==1){
                    oss << default_values[i]*(1+value);
                }else if(mode==2){
                    oss << default_values[i]+value;
                }else{
                    oss << value;
                }
            }
            
        }
        return oss.str();
    }
}

// Helper function to extract a substring
std::string extractField(const std::string& line, size_t start, size_t width) {
    if (start >= line.size()) {
        return ""; // 超过行长度，返回空
    }
    return line.substr(start, width);
}

// Convert a substring to a double, treating empty or invalid fields as 0
double parseField(const std::string& field) {
    try {
        return std::stod(field); // 尝试转换为 double
    } catch (const std::invalid_argument&) {
        return 0.0; // 空字段或无效值，返回 0
    }
}

void readFormattedData(const std::string& line, std::vector<double>& data) {
    // Define the positions and widths for relevant fields (ignoring 1x, 5x, etc.)
    // (1x,i2,1x,i2,5x,i4,1x,i2,1x,i4,1x,i3,1x,f6.2,1x,f12.5,1x,
    //  &        f6.2,1x,f11.5,1x,f8.2,1x,f6.2,1x,16f5.2)
    const std::vector<std::pair<size_t, size_t>> fieldPositions = {
        {1, 2},   // i2
        {4, 2},   // i2
        {11, 4},  // i4
        {16, 2},  // i2
        {19, 4},  // i4
        {24, 3},  // i3
        {28, 6},  // f6.2
        {35, 12}, // f12.5
        {48, 6},  // f6.2
        {55, 11}, // f11.5
        {67, 8},  // f8.2
        {76, 6}  // f6.2
    };

    for (const auto& [start, width] : fieldPositions) {
        // Extract the field
        std::string field = extractField(line, start, width);
        data.push_back(parseField(field)); // Convert and store the value
    }
}

void _write_value(const std::string file_path, const std::string file_name, const std::vector<std::string> var_list, std::map<std::string, std::string> default_value, 
                      const std::vector<int> var_index, const std::vector<int> var_mode, 
                      const std::vector<std::string> position_list, const std::vector<int> type_list,
                      const py::array_t<double> input_values, std::vector<int> sol_layer){
    
    std::regex pattern(R"((.*)\.(.*))");
    std::smatch match;
    std::regex_search(file_name, match, pattern);
    std::string file_extension = match[2].str();
    
    std::string new_file_path=match[1].str()+file_extension+".tmp";

    fs::path file_to_open = fs::path(file_path) / file_name;
    fs::path file_to_save = fs::path(file_path) / new_file_path;
    std::ifstream file(file_to_open);
    std::ofstream new_file(file_to_save);

    std::vector<std::string> lines;
    std::string line;
    std::vector<std::regex> patterns;
    std::vector<int> sign(var_list.size(), 1);

    if (file_extension == "sol"){
        //sol file
        for (const auto varname : var_list) {
            // std::string p = std::format(R"(\s*({})(.*:\s+)(.*))", varname);
            std::string p =  R"(\s*()" + varname + R"()(.*:\s+)(.*))";
            patterns.emplace_back(p);
            }
        
        std::regex float_regex("([-+]?[0-9]*\\.?[0-9]+)");
        auto replace_numbers = [&float_regex](const std::string& line, const std::vector<double>& values) {
            std::string& modifiable_line = const_cast<std::string&>(line);
            std::ostringstream output;
            std::regex_iterator<std::string::iterator> it(modifiable_line.begin(), modifiable_line.end(), float_regex);
            std::regex_iterator<std::string::iterator> end;
            size_t value_index = 0;
            size_t last_pos = 0;

            while (it != end) {
                output << line.substr(last_pos, it->position() - last_pos);
                if (value_index < values.size()) {
                    output << values[value_index++];
                } else {
                    output << it->str(); 
                }
                last_pos = it->position() + it->length();
                ++it;
            }
            output << line.substr(last_pos); 

            return output.str();
        };
        while (std::getline(file, line)) {
            for (size_t i = 0; i < patterns.size(); ++i) {
                std::smatch match;
                if (sign[i] && std::regex_search(line, match, patterns[i])) {
                    //line=replace_numbers(line, results.at(varname_list[i]));
                    // std::cout<<var_list[i]<<" "<<line<<" "<<var_index[i]<<" "<<input_values.at(var_index[i])<<std::endl;
                    // std::cout<<default_value[i]<<std::endl;
                    std::string result=_generate_value(default_value[var_list[i]], var_mode[i], input_values.at(var_index[i]), sol_layer[i]);
                    // std::cout<<result<<std::endl;
                    line=std::regex_replace(line, patterns[i], match[1].str()+match[2].str()+result);
                    sign[i] = 0;
                    }
                }
            new_file << line << std::endl;
        }
    }else if (file_extension=="ops")
    {
        std::vector<std::string> lines_;
        std::string line_;
        while (std::getline(file, line_)) {
            lines_.push_back(line_);
        }

        for (int i = 0; i < var_list.size(); ++i) {
            auto position=position_list[i];
            std::istringstream iss(position);
            std::string tmp1, tmp2;
            std::getline(iss, tmp1, '_');
            std::getline(iss, tmp2);
            int row, col;
            row = std::stoi(tmp1);
            col = std::stoi(tmp2);
            
            const std::string isss=lines_[row-1];
            // iss = std::istringstream(lines_[row-1]);
            std::vector<double> numbers;
            // std::string num;
            readFormattedData(isss, numbers);
            // while (iss >> num){
            //     numbers.push_back(num);
            // }

            //0 denote int; 1 denote string
            if(type_list[i]==0){
                int intValue=static_cast<int>(input_values.at(var_index[i]));
                double strValue=static_cast<double>(intValue);
                numbers[col-1]=strValue;
            }else{
                double doubleValue=input_values.at(var_index[i]);
                // std::string strValue=std::to_string(doubleValue);
                double strValue=doubleValue;
                numbers[col-1]=strValue;
            }

            // std::ostringstream oss;
            // oss << std::right;

            // 根据 vector 的大小动态格式化输出
            // if (numbers.size() >= 1) {
            //     oss << std::setw(3) << std::stoi(numbers[0]); // 1x, i2 (2字符宽度)
            // }
            // if (numbers.size() >= 2) {
            //     oss << std::setw(3) << std::stoi(numbers[1]); // 1x, i2
            // }
            // if (numbers.size() >= 3) {
            //     oss << std::setw(9) << std::stoi(numbers[2]); // 5x, i4
            // }
            // if (numbers.size() >= 4) {
            //     oss << std::setw(3) << std::stoi(numbers[3]); // 1x, i2
            // }
            // if (numbers.size() >= 5) {
            //     oss << std::setw(5) << std::stoi(numbers[4]); // 1x, i4
            // }
            // if (numbers.size() >= 6) {
            //     oss << std::setw(4) << std::stoi(numbers[5]); // 1x, i3
            // }
            // if (numbers.size() >= 7) {
            //     oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[6]); // 1x, f6.2
            // }
            // if (numbers.size() >= 8) {
            //     oss << std::setw(13) << std::fixed << std::setprecision(5) << std::stof(numbers[7]); // 1x, f12.5
            // }
            // if (numbers.size() >= 9) {
            //     oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[8]); // 1x, f6.2
            // }
            // if (numbers.size() >= 10) {
            //     oss << std::setw(12) << std::fixed << std::setprecision(5) << std::stof(numbers[9]); // 1x, f11.5
            // }
            // if (numbers.size() >= 11) {
            //     oss << std::setw(9) << std::fixed << std::setprecision(2) << std::stof(numbers[10]); // 1x, f8.2
            // }
            // if (numbers.size() >= 12) {
            //     oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[11]); // 1x, f6.2
            // }

            std::ostringstream oss;
            oss<< std::right;
            oss << std::setw(3) << static_cast<int>(numbers[0]) // 1x, i2 (2字符宽度)
              << std::setw(3) << static_cast<int>(numbers[1])  // 1x, i2
              << std::setw(9) << static_cast<int>(numbers[2]) // 5x, i4
              << std::setw(3) << static_cast<int>(numbers[3])  // 1x, i2
              << std::setw(5) << static_cast<int>(numbers[4]) // 1x, i4
              << std::setw(4) << static_cast<int>(numbers[5]) // 1x, i3
              << std::setw(7) << std::fixed << std::setprecision(2) << numbers[6] // 1x, f6.2
              << std::setw(13) << std::fixed << std::setprecision(5) << numbers[7] // 1x, f12.5
              << std::setw(7) << std::fixed << std::setprecision(2) << numbers[8] // 1x, f6.2
              << std::setw(12) << std::fixed << std::setprecision(5) << numbers[9] // 1x, f11.5
              << std::setw(9) << std::fixed << std::setprecision(2) << numbers[10] // 1x, f8.2
              << std::setw(7) << std::fixed << std::setprecision(2) << numbers[11]; // 1x, f6.2
            lines_[row-1]=oss.str();
        }

        for (auto& line : lines_) {
            new_file << line << std::endl;
        }

    }else{
                //ordinary file
        for (const auto varname : var_list) {
            std::string p = R"((\s*)(-?\d+\.\d+)(\s*\|\s*)" + varname + R"())";
            patterns.emplace_back(p);
        }

        while (std::getline(file, line)) {
            for (size_t i = 0; i < patterns.size(); ++i) {
                std::smatch match;
                if (sign[i] && std::regex_search(line, match, patterns[i])) {
                    std::string result=_generate_value(default_value[var_list[i]], var_mode[i], input_values.at(var_index[i]), sol_layer[i]);
                    // line=std::regex_replace(line, patterns[i], match[1].str()+std::format("{}", result)+match[3].str());
                    line = std::regex_replace(line, patterns[i], match[1].str() + result + match[3].str());
                    sign[i] = 0;
                    }
                }
            new_file << line << std::endl;
            }
    }
    file.close();
    new_file.close();
    fs::path old_file = fs::path(file_path) / file_name;
    fs::path new_file_ = fs::path(file_path) / new_file_path;

    fs::remove(old_file);          // 删除旧文件（如果存在）
    fs::rename(new_file_, old_file); // 重命名新文件为旧文件名

}




std::unordered_map<std::string, std::vector<double>> _read_value_swat(const std::string& file_path, const std::string &file_name, 
                    const std::vector<std::string>& varname_list, const std::vector<std::string>& position_list, const int &mode) {
    
    fs::path file_to_open = fs::path(file_path) / file_name;
    std::ifstream file(file_to_open.string());

    if (!file.is_open()) {
        throw py::value_error("The file does not exist");
    }
    //
    std::regex pattern(R"(.*\.(.*))");
    std::smatch match;
    std::regex_search(file_name, match, pattern);
    std::string file_extension = match[1].str();
    
    std::unordered_map<std::string, std::vector<double>> results;
    std::string line;
    std::vector<std::regex> patterns;
    std::vector<int> sign(varname_list.size(), 1);

    if (file_extension == "sol"){

        for (const auto& varname : varname_list) {
        // std::string p = std::format(R"(\s*({}).*)", varname);
        std::string p = R"(\s*()" + varname + R"().*)";
        patterns.emplace_back(p);
        }

        std::regex float_regex("([-+]?[0-9]*\\.?[0-9]+)");

        auto extract_floats = [&float_regex](const std::string& line, std::vector<double>& values) {
            auto begin = std::sregex_iterator(line.begin(), line.end(), float_regex);
            auto end = std::sregex_iterator();

            for (std::sregex_iterator i = begin; i != end; ++i) {
                    std::smatch match = *i;
                    double num = std::stod(match.str());
                    values.push_back(num);
                }
        };

        while (std::getline(file, line)) {
            for (size_t i = 0; i < patterns.size(); ++i) {
                std::smatch match;
                if (sign[i] && std::regex_search(line, match, patterns[i])) {
                    if (mode==0){
                        extract_floats(line, results[varname_list[i]]);
                    }else{
                        extract_floats(line, results[varname_list[i]+"|"+file_name]);
                    }
                    // std::cout<<line<<" "<<varname_list[i]<<std::endl;
                    sign[i] = 0;
                    }
                }
        }
    }else if (file_extension == "ops"){

        std::vector<std::string> lines_;
        std::string line_;
        while (std::getline(file, line_)) {
            lines_.push_back(line_);
        }
        for (int i = 0; i < varname_list.size(); ++i) {
            auto position=position_list[i];
            std::istringstream iss(position);
            std::string tmp1, tmp2;
            std::getline(iss, tmp1, '_');
            std::getline(iss, tmp2);
            int row, col;
            row = std::stoi(tmp1);
            col = std::stoi(tmp2);
            
            std::string isss=lines_[row-1];
            std::vector<double> numbers;
            readFormattedData(isss, numbers);

            if(mode==0){
                results[varname_list[i]].push_back(numbers[col-1]);
            }else{
                results[varname_list[i]+"|"+file_name].push_back(numbers[col-1]);
            }
        }
    }else{
        
        for (int i = 0; i < varname_list.size(); ++i) {
            const auto& varname = varname_list[i];
            std::string p = R"(\s*(-?\d*\.?\d*?)\s*\|\s*)" + varname;
            // std::string p = std::format(R"(\s*(-?\d*\.?\d*?)\s*\|\s*{})", varname);
            patterns.emplace_back(p);
        }

        while (std::getline(file, line)) {
            for (size_t i = 0; i < patterns.size(); ++i) {
                std::smatch match;
                if (sign[i] && std::regex_search(line, match, patterns[i])) {
                    
                    if(mode==0){
                        results[varname_list[i]].push_back(std::stod(match[1].str()));
                    }else{
                        results[varname_list[i]+"|"+file_name].push_back(std::stod(match[1].str()));
                    }
                    sign[i] = 0;
                    }
                }
        }
    }
    return results;
}

std::vector<double> _read_simulation(const std::string& file_path, int col, int rch_id, int rch_total, int start_line, int end_line) {
    std::ifstream file(file_path);
    std::string line;
    std::vector<double> data;

    int lineCount = 0;
    int rch_count = 0;

    if (rch_total == rch_id) {
        rch_id=0;
    }

    while (getline(file, line)){
        ++lineCount;
        if(lineCount<start_line) continue;
        if(lineCount>end_line) break;

        ++rch_count;
        if(rch_count%rch_total!=rch_id) continue;
        std::istringstream iss(line);
        std::string temp;
        int columnCount=0;
        double value;

        while (iss >> temp){
            ++columnCount;
            if(columnCount==col){
                std::istringstream(temp) >> value;
                data.push_back(value);
            }
        }

    }
    file.close();

    return data;
}

void _copy_origin_to_tmp(const std::string &source, const std::string &destination){
    fs::copy(source, destination, fs::copy_options::recursive);
}

PYBIND11_MODULE(utility, m) {

    py::class_<SwatFileHandler>(m, "SwatFileHandler")
        .def(py::init<const std::string&>());

    m.def("createFileHandler", &createFileHandler, 
          "Create a SwatFileHandler instance (returns a managed pointer)", 
          py::call_guard<py::gil_scoped_release>());

    m.def("set_value_FileHandler", &set_value_FileHandler, 
          "Modify values using the handler and save to file", 
          py::call_guard<py::gil_scoped_release>());
    
    m.doc() = "Swat utility plugin";
    m.def("read_value_swat", &_read_value_swat, "A function that reads and processes file data based on regex patterns.", py::call_guard<py::gil_scoped_release>());
    m.def("read_simulation", &_read_simulation, "A function that reads the 6th column from a file and returns as a numpy array",
          py::call_guard<py::gil_scoped_release>());
    m.def("copy_origin_to_tmp", &_copy_origin_to_tmp, "A function that copies the origin folder to the tmp folder", py::call_guard<py::gil_scoped_release>());
    m.def("write_value_to_file", &_write_value, "A function that writes the value to the file", py::call_guard<py::gil_scoped_release>());
}
