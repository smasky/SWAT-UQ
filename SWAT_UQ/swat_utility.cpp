#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <regex>
#include <memory>
#include <format>
#include <unordered_map>
#include <sstream>
#include <filesystem>
#include <iomanip>
#include <cstdio>
#include <exception>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
namespace fs = std::filesystem;

std::string _generate_value(const std::string &default_value_str, const int &mode, const double &value, const int &M){
    
    // auto value_tuple = var_infos[var_name.c_str()].cast<py::tuple>();
    // int index=value_tuple[0].cast<int>();
    // std::string mode=value_tuple[1].cast<std::string>();
    
    // std::string default_value_str=default_value[var_name.c_str()].cast<std::string>();
    // double value=input_values.at(index);
    
    double result;
    if (M==0){
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
            
            if(mode==1){
                oss << default_values[i]*(1+value);
            }else if(mode==2){
                oss << default_values[i]+value;
            }else{
                oss << value;
            }
        }
        return oss.str();
    }else{
        double default_value=std::stod(default_value_str);
        if (mode==1){
            result=default_value*(1+value);
        }else if(mode==2){
            result=default_value+value;
        }else{
            result=value;
        }
        return std::to_string(result);
    }
}


void _write_value(const std::string file_path, const std::string file_name, const std::vector<std::string> var_list, const std::vector<std::string> default_value, 
                      const std::vector<int> var_index, const std::vector<int> var_mode, 
                      const std::vector<std::string> position_list, const std::vector<int> type_list,
                      const py::array_t<double> input_values){
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
            std::string p = std::format(R"(\s*({})(.*:\s+)(.*))", varname);
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
                    std::string result=_generate_value(default_value[i], var_mode[i], input_values.at(var_index[i]), 0);
                    line=std::regex_replace(line, patterns[i], match[1].str()+match[2].str()+std::format("{}", result));
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
            
            iss = std::istringstream(lines_[row-1]);
            std::vector<std::string> numbers;
            std::string num;
            while (iss >> num){
                numbers.push_back(num);
            }

            //0 denote int; 1 denote string
            if(type_list[i]==0){
                int intValue=static_cast<int>(input_values.at(var_index[i]));
                std::string strValue=std::to_string(intValue);
                numbers[col-1]=strValue;
            }else{
                double doubleValue=input_values.at(var_index[i]);
                std::string strValue=std::to_string(doubleValue);
                numbers[col-1]=strValue;
            }

            std::ostringstream oss;
            oss<< std::right;
            if (numbers.size() > 0) oss << std::setw(3) << std::stoi(numbers[0]);
            if (numbers.size() > 1) oss << std::setw(3) << std::stoi(numbers[1]);
            if (numbers.size() > 2) oss << std::setw(9) << std::stoi(numbers[2]);
            if (numbers.size() > 3) oss << std::setw(3) << std::stoi(numbers[3]);
            if (numbers.size() > 4) oss << std::setw(5) << std::stoi(numbers[4]);
            if (numbers.size() > 5) oss << std::setw(4) << std::stoi(numbers[5]);
            if (numbers.size() > 6) oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[6]);
            if (numbers.size() > 7) oss << std::setw(13) << std::fixed << std::setprecision(5) << std::stof(numbers[7]);
            if (numbers.size() > 8) oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[8]);
            if (numbers.size() > 9) oss << std::setw(12) << std::fixed << std::setprecision(5) << std::stof(numbers[9]);
            if (numbers.size() > 10) oss << std::setw(9) << std::fixed << std::setprecision(2) << std::stof(numbers[10]);
            if (numbers.size() > 11) oss << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[11]);
            // oss << std::setw(3) << std::stoi(numbers[0]) // 1x, i2 (2字符宽度)
            //   << std::setw(3) << std::stoi(numbers[1])  // 1x, i2
            //   << std::setw(9) << std::stoi(numbers[2]) // 5x, i4
            //   << std::setw(3) << std::stoi(numbers[3])  // 1x, i2
            //   << std::setw(5) << std::stoi(numbers[4]) // 1x, i4
            //   << std::setw(4) << std::stoi(numbers[5]) // 1x, i3
            //   << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[6]) // 1x, f6.2
            //   << std::setw(13) << std::fixed << std::setprecision(5) << std::stof(numbers[7]) // 1x, f12.5
            //   << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[8]) // 1x, f6.2
            //   << std::setw(12) << std::fixed << std::setprecision(5) << std::stof(numbers[9]) // 1x, f11.5
            //   << std::setw(9) << std::fixed << std::setprecision(2) << std::stof(numbers[10]) // 1x, f8.2
            //   << std::setw(7) << std::fixed << std::setprecision(2) << std::stof(numbers[11]); // 1x, f6.2
            lines_[row-1]=oss.str();
        }

        for (auto& line : lines_) {
            new_file << line << std::endl;
        }

    }else{
                //ordinary file
        for (const auto varname : var_list) {
            std::string p = std::format(R"((\s*)(-?\d+\.\d+)(\s*\|\s*{}))", varname);
            patterns.emplace_back(p);
        }

        while (std::getline(file, line)) {
            for (size_t i = 0; i < patterns.size(); ++i) {
                std::smatch match;
                if (sign[i] && std::regex_search(line, match, patterns[i])) {
                    std::string result=_generate_value(default_value[i], var_mode[i], input_values.at(var_index[i]), 1);
                    line=std::regex_replace(line, patterns[i], match[1].str()+std::format("{}", result)+match[3].str());
                    sign[i] = 0;
                    }
                }
            new_file << line << std::endl;
            }
    }
    file.close();
    new_file.close();

    std::string old_file=file_path+"/"+file_name;
    std::string new_file_=file_path+"/"+new_file_path;
    std::remove(old_file.c_str());
    std::rename(new_file_.c_str(), old_file.c_str());
}

std::unordered_map<std::string, std::vector<double>> _read_value_swat(const std::string& file_path, const std::string &file_name, 
                    const std::vector<std::string>& varname_list, const std::vector<std::string>& position_list, const int &mode) {
    fs::path file_to_open = fs::path(file_path) / file_name;
    std::ifstream file(file_to_open);
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
        std::string p = std::format(R"(\s*({}).*)", varname);
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
            
            iss = std::istringstream(lines_[row-1]);
            std::vector<double> numbers;
            double num;
            while (iss >> num){
                numbers.push_back(num);
            }
            if(mode==0){
                results[varname_list[i]].push_back(numbers[col-1]);
            }else{
                results[varname_list[i]+"|"+file_name].push_back(numbers[col-1]);
            }
        }
    }else{
        
        for (int i = 0; i < varname_list.size(); ++i) {
            const auto& varname = varname_list[i];
            std::string p = std::format(R"(\s*(-?\d*\.?\d*?)\s*\|\s*{})", varname);
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

// void _set_value_swat(const std::string& file_path, const std::vector<std::string>& varname_list, const std::unordered_map<std::string, std::string> results) {
//     std::regex pattern(R"((.*)\.(.*))");
//     std::smatch match;
//     std::regex_search(file_path, match, pattern);
//     std::string file_extension = match[2].str();

//     std::string new_file_path=match[1].str()+".new";

//     std::ifstream file(file_path);
//     std::ofstream new_file(new_file_path);

//     if (!file.is_open()) {
//         throw py::value_error("The file does not exist");
//     }
//     //
//     std::vector<std::string> lines;
//     std::string line;
//     std::vector<std::regex> patterns;
//     std::vector<int> sign(varname_list.size(), 1);

//     if (file_extension == "sol"){

//          for (const auto& varname : varname_list) {
//             std::string p = std::format(R"(\s*({})(.*:\s+)(.*))", varname);
//             patterns.emplace_back(p);
//             }
//         // 定义一个lambda表达式来处理替换操作
//         std::regex float_regex("([-+]?[0-9]*\\.?[0-9]+)");
//         auto replace_numbers = [&float_regex](const std::string& line, const std::vector<double>& values) {
//             std::string& modifiable_line = const_cast<std::string&>(line);
//             std::ostringstream output;
//             std::regex_iterator<std::string::iterator> it(modifiable_line.begin(), modifiable_line.end(), float_regex);
//             std::regex_iterator<std::string::iterator> end;
//             size_t value_index = 0;
//             size_t last_pos = 0;

//             while (it != end) {
//                 output << line.substr(last_pos, it->position() - last_pos);
//                 if (value_index < values.size()) {
//                     output << values[value_index++];
//                 } else {
//                     output << it->str(); // 如果没有更多的替换值，保留原始数字
//                 }
//                 last_pos = it->position() + it->length();
//                 ++it;
//             }
//             output << line.substr(last_pos); // 添加最后一部分

//             return output.str();
//         };
//         while (std::getline(file, line)) {
//             for (size_t i = 0; i < patterns.size(); ++i) {
//                 std::smatch match;
//                 if (sign[i] && std::regex_search(line, match, patterns[i])) {
//                     //line=replace_numbers(line, results.at(varname_list[i]));
//                     line=std::regex_replace(line, patterns[i], match[1].str()+match[2].str()+std::format("{}", results.at(varname_list[i])));
//                     sign[i] = 0;
//                     }
//                 }
//             new_file << line << std::endl;
//         }

//     }else{

//         for (const auto& varname : varname_list) {
//             std::string p = std::format(R"((\s*)(-?\d+\.\d+)(\s*\|\s*{}))", varname);
//             patterns.emplace_back(p);
//         }

//          while (std::getline(file, line)) {
//             for (size_t i = 0; i < patterns.size(); ++i) {
//                 std::smatch match;
//                 if (sign[i] && std::regex_search(line, match, patterns[i])) {
//                     line=std::regex_replace(line, patterns[i], match[1].str()+std::format("{}", results.at(varname_list[i]))+match[3].str());
//                     sign[i] = 0;
//                     }
//                 }
//             new_file << line << std::endl;
//         }

//     }

//     file.close();
//     new_file.close();

//     std::remove(file_path.c_str());
//     std::rename(new_file_path.c_str(), file_path.c_str());

// }

std::vector<double> _read_simulation(const std::string& file_path, int col, int rch_id, int rch_total, int start_line, int end_line) {
    std::ifstream file(file_path);
    std::string line;
    std::vector<double> data;

    if (rch_id==rch_total){
        rch_id=0;
    }

    int lineCount = 0;
    int rch_count = 0;
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

PYBIND11_MODULE(swat_utility, m) {
    m.doc() = "Swat utility plugin"; // 可选的模块文档字符串
    m.def("read_value_swat", &_read_value_swat, "A function that reads and processes file data based on regex patterns.", py::call_guard<py::gil_scoped_release>());
    // m.def("set_value_swat", &_set_value_swat, "A function that sets and processes file data based on regex patterns.", py::call_guard<py::gil_scoped_release>());
    m.def("read_simulation", &_read_simulation, "A function that reads the 6th column from a file and returns as a numpy array",
          py::call_guard<py::gil_scoped_release>());
    m.def("copy_origin_to_tmp", &_copy_origin_to_tmp, "A function that copies the origin folder to the tmp folder", py::call_guard<py::gil_scoped_release>());
    m.def("write_value_to_file", &_write_value, "A function that writes the value to the file", py::call_guard<py::gil_scoped_release>());
}
