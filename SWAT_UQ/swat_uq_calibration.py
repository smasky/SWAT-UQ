import os
import re
import queue
import shutil
import tempfile
import itertools
import subprocess
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from UQPyL.problems import ProblemABC as Problem
from concurrent.futures import ThreadPoolExecutor

#C++ Module
from .swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation

from .metric import OBJ_FUNC

VARNAME={6: "FLOW_OUT", 47: "TOT_N", 48: "TOT_P" }
OBJ_TYPE_NAME={1: "NSE", 2:"RMSE", 3:"PCC", 4:"Pbias", 5:"KGE"}

HRU_SUFFIX=["chm", "gw", "hru", "mgt", "sdr", "sep", "sol"]
WATERSHED_SUFFIX=["pnd", "rte", "sub", "swq", "wgn", "wus"]

class SWAT_UQ_Calibration(Problem):
    
    model={}
    observe={}
    
    def __init__(self, work_path: str, paraInfos_name: str, 
                 observed_file_name: str, swat_exe_name: str, temp_path:str=None, 
                 max_threads: int=12, num_parallel: int=5, verboseFlag=False):
        
        #set verbose Flag
        self.verboseFlag=verboseFlag
        
        #create the space for running multiple instance of SWAT
        if temp_path is None:
            #if dont set the temp_path, create a temp dir
            self.work_temp_dir=tempfile.mkdtemp()
            self.use_temp_dir=True
            print("Temporary directory has been created in: ", self.work_temp_dir) if self.verboseFlag else None
        else:
            now_time=datetime.now().strftime("%m%d_%H%M%S")
            temp_path=os.path.join(temp_path, now_time)
            os.makedirs(temp_path)
            self.work_temp_dir=temp_path
            self.use_temp_dir=False
            
        #basic setting
        self.work_path=work_path
        self.paraInfos_name=paraInfos_name
        self.observed_file_name=observed_file_name
        self.swat_exe_name=swat_exe_name
        
        self.max_workers=max_threads
        self.num_parallel=num_parallel
        
        if self.verboseFlag:
            print("="*25+"basic setting"+"="*25)
            print("The path of SWAT project is: ", self.work_path)
            print("The file name of optimizing parameters is: ", self.paraInfos_name)
            print("The file name of observed data is: ", self.observed_file_name)
            print("The name of SWAT executable is: ", self.swat_exe_name)
            print("Temporary directory has been created in: ", self.work_temp_dir)
            print("="*70)
            print("\n"*2)
        
        #Initialize the Swat project
        self._initial()
        #input variables
        self._record_default_values()
        #output objective
        self._get_observed_data()
        
        self.work_path_queue=queue.Queue()
        self.work_temp_dirs=[]
        
        for i in range(num_parallel):
            path=os.path.join(self.work_temp_dir, "instance{}".format(i))
            self.work_temp_dirs.append(path)
            self.work_path_queue.put(path)
                
        with ThreadPoolExecutor(max_workers=self.num_parallel) as executor:
            futures = [executor.submit(copy_origin_to_tmp, self.work_path, work_temp) for work_temp in self.work_temp_dirs]
        for future in futures:
            future.result()
                       
        super().__init__(nInput=self.nInput, nOutput=self.nOutput, lb=self.lb, ub=self.ub, var_type=[0]*self.nInput, var_set=None, x_labels=self.x_labels)
    
    #------------------------interface function-----------------------#
    def _subprocess(self, xInput, id):
        
        work_path=self.work_path_queue.get()
        self._set_values(work_path, xInput)
        
        process= subprocess.Popen(
            os.path.join(work_path, self.swat_exe_name),
            cwd=work_path,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True)
        
        process.wait()
        
        total_objs=self.nOutput
        data_infos=self.observe["observe_data"]
        obj_comb=self.observe["obj_comb"]
        
        obj_array=np.zeros(total_objs)
        
        for obj_id in range(1, total_objs+1):
            series_comb=obj_comb[obj_id]
            v_obj=0
            for series_id in series_comb:
                data_info=data_infos[series_id-1]
                rch_id=data_info[1]
                var_col=data_info[2]
                obj_type=data_info[3]
                obj_id=data_info[4]
                weight=data_info[5]
                read_lines=data_info[6]
                observed_value=data_info[7]
                
                sim_value_list=[]
                for lines in read_lines:
                    startline=int(lines[0])
                    endline=lines[1]
                    sub_value=np.array(read_simulation(os.path.join(work_path, "output.rch"), var_col+1, rch_id, self.model['n_rch'], startline, endline))
                    sim_value_list.append(sub_value)
                sim_value=np.concatenate(sim_value_list, axis=0)
                obj_value=OBJ_FUNC[obj_type](observed_value, sim_value)
                v_obj+=obj_value*weight
            obj_array[obj_id-1]=v_obj
            
        self.work_path_queue.put(work_path)
        return (id, obj_array)
    
    def evaluate(self, X):
        nSample, _ =X.shape
        Y=np.zeros( (nSample, self.nOutput) )
        
        if nSample<self.num_parallel:
            for i in range(nSample):
                id, obj_value=self._subprocess(X[i,:], i)
                Y[id, :]=obj_value
        else:
            with ThreadPoolExecutor(max_workers=self.num_parallel) as executor:
                futures=[executor.submit(self._subprocess, X[i, :], i) for i in range(nSample)]
            
            for i, future in enumerate(futures):
                 id, obj_value=future.result()
                 Y[id, :]=obj_value
                  
        return Y
    #---------------------private function------------------------------#
    def _initial(self): 
        
        paras=["IPRINT", "NBYR", "IYR", "IDAF", "IDAL", "NYSKIP"]
        pos=["default"]*len(paras)
        
        dict_values=read_value_swat(self.work_path, "file.cio", paras, pos, 0)
        begin_date=datetime(int(dict_values["IYR"][0]), 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)
        end_date=datetime(int(dict_values["IYR"][0])+int(dict_values['NBYR'][0])-1, 1, 1)+timedelta(int(dict_values['IDAL'][0])-1)
        simulation_days=(end_date-begin_date).days+1
        output_skip_years=int(dict_values["NYSKIP"][0])
        output_skip_days=(datetime(int(dict_values["IYR"][0])+output_skip_years, 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)-begin_date).days
        begin_record=begin_date+timedelta(output_skip_days)
        
        self.model["print_flag"]=int(dict_values["IPRINT"][0])
        self.model["begin_date"]=begin_date
        self.model["end_date"]=end_date
        self.model["output_skip_years"]=output_skip_years
        self.model["simulation_days"]=simulation_days
        self.model["begin_record"]=begin_record
        
        #read control file fig.fig
        watershed={}
        with open(os.path.join(self.work_path, "fig.fig"), "r") as f:
            lines=f.readlines()
            for line in lines:
                match = re.search(r'(\d+)\.sub', line)
                if match:
                    watershed[match.group(1)]=[]
        
        #read sub files
        for sub in watershed:
            file_name=sub+".sub"
            with open(os.path.join(self.work_path, file_name), "r") as f:
                lines=f.readlines()
                for line in lines:
                    match = re.search(r'(\d+)\.mgt', line)
                    if match:
                        watershed[sub].append(match.group(1))
        
        self.model["watershed_list"]=list(watershed.keys())
        self.model["hru_list"] = list(itertools.chain.from_iterable(watershed.values()))
        self.model["watershed_hru"]=watershed
        self.model["n_hru"]=len(self.model["hru_list"])
        self.model["n_watershed"]=len(self.model["watershed_list"])
        self.model["n_rch"]=len(self.model["watershed_list"])
        
        self.paraInfos=pd.read_excel(os.path.join(self.work_path, 'SWAT_paras_files.xlsx'), index_col=0)

        if self.verboseFlag:
            print("="*25+"Model Information"+"="*25)
            print("The time period of simulation is: ", self.model["begin_date"].strftime("%Y%m%d"), " to ", self.model["end_date"].strftime("%Y%m%d"))
            print("The number of simulation days is: ", self.model["simulation_days"])
            print("The number of output skip years is: ", self.model["output_skip_years"])
            print("The number of HRUs is: ", self.model["n_hru"])
            print("The number of Reaches is: ", self.model["n_rch"])
            if self.model["print_flag"]==0:
                print("The print flag of SWAT is: ", "monthly")
            else:
                print("The print flag of SWAT is: ", "daily")
            print("="*70)
            print("\n"*1)
            
    def __del__(self):
        if self.used_temp_dir:
            os.makedirs(self.work_temp_dir)
    
    def _set_values(self, work_path, paras_values):
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures=[]
            for file_name, infos in self.model["file_var_info"].items():
                future = executor.submit(write_value_to_file, work_path, file_name, 
                                         infos["name"], infos["default"], 
                                         infos["index"], infos["mode"],  infos["position"], infos["type"],
                                         paras_values.ravel())
                futures.append(future)
            
            for future in futures:
                res=future.result()
              
    def _get_observed_data(self):
        
        file_path=os.path.join(self.work_path, self.observed_file_name)
        rch_ids=[]
        var_cols=[]
        rch_weights=[]
        obj_types=[]
        data=[]
        
        print_flag=self.model["print_flag"]
        
        try:
            with open(file_path, "r") as f:
                
                lines=f.readlines()
                
                pattern_id=re.compile(r'REACH_ID_(\d+)\s+')
                pattern_col=re.compile(r'VAR_COL_(\d+)\s+')
                pattern_type=re.compile(r'TYPE_(\d+)\s+')
                pattern_obj=re.compile(r'OBJ_(\d+)\s+')
                pattern_value=re.compile(r'(\d+)\s+[a-zA-Z]*_?OUT_(\d+)_(\d+)\s+(\d+\.?\d*)')
                
                total_series=int(re.search(r'\d+', lines[0]).group()) #read the num of reaches
                num_objs=int(re.search(r'\d+', lines[1]).group())
                
                obj_comb={}
                obj_ids=[]
                for i in range(1, num_objs+1):
                    obj_comb.setdefault(i, [])
                
                i=2; series_id=0
                while i<len(lines):
                    line=lines[i]
                    match_rch= pattern_id.match(line)
                    if match_rch:
                        series_id+=1
                        
                        rch_id=int(match_rch.group(1))
                        rch_ids.append(rch_id)
                        
                        var_col=int(pattern_col.match(lines[i+1]).group(1))
                        var_cols.append(var_col)
                        
                        obj_type=int(pattern_type.match(lines[i+2]).group(1))
                        obj_types.append(obj_type)
                        
                        obj_id=int(pattern_obj.match(lines[i+3]).group(1))
                        obj_comb[obj_id].append(series_id)
                        obj_ids.append(obj_id)
                        
                        weight=float(re.search(r'\d+\.?\d*',lines[i+4]).group())
                        rch_weights.append(weight)
                        
                        num_data=int(re.search(r'\d+', lines[i+5]).group())
                        
                        i=i+6
                        
                        line=lines[i]
                        while pattern_value.match(line) is None:
                            i+=1
                            line=lines[i]   
                            
                        n=0
                        while True:
                            line=lines[i];n+=1
                            match_data = pattern_value.match(line)
                            _, time, year = map(int, match_data.groups()[:-1])
                            value = float(match_data.groups()[-1])
                            if print_flag==0:
                                years=year-self.model["begin_date"].year
                                if years==0:
                                    index=time-self.model["begin_date"].month
                                else:
                                    index=time+12-self.model["begin_date"].month+(years-1)*12
                            else:
                                index=(datetime(year, 1, 1)+timedelta(days=time-1)-self.model["begin_record"]).days
                            data.append([series_id, rch_id, var_col, obj_type, obj_id, weight, int(index), int(year), int(time), value])
                            if n==num_data:
                                break
                            else:
                                i+=1              
                    i+=1
        except FileNotFoundError:
            raise FileNotFoundError("The observed data file is not found, please check the file name!")
        
        except Exception as e:
            raise ValueError("There is an error in observed data file, please check!")
        
        if total_series!=series_id:
            raise ValueError("The number of reaches in observed.txt is not equal to the number of reaches in flow data!")
        
        observed_data = pd.DataFrame(data, columns=['series_id', 'rch_id', 'var_col', 'obj_type', 'obj_id', 'weight','index', 'year', 'time', 'value'])
                                     
        data_infos=[]
        for series_id in range(0, total_series):
            id=series_id+1
            data=observed_data.query('series_id==@id')
            data_value=data['value'].to_numpy(dtype=float)
            data_index=data['index'].to_numpy(dtype=int)
            read_lines=self._get_lines_for_output(data_index)
            data_infos.append((series_id, rch_ids[series_id], var_cols[series_id], obj_types[series_id], obj_ids[series_id], rch_weights[series_id],  read_lines, data_value))

        self.observe["total_series"]=total_series
        self.observe["observe_data"]=data_infos
        self.observe["obj_comb"]=obj_comb
        self.nOutput=num_objs

        if self.verboseFlag:
            print("="*25+"Observed Information"+"="*25)
            print("The number of observed data series is: ", total_series)
            print("The number of objective functions is: ", num_objs)
            series_id_formatted="{:^10}".format("Series_id")
            rch_formatted="{:^10}".format("Reach_id")
            variable_formatted= "{:^10}".format("Variable")
            obj_type_formatted= "{:^10}".format("Obj_type")
            obj_id_formatted= "{:^10}".format("Obj_id")
            weight_formatted= "{:^10}".format("Weight")
            data_formatted= "{:<30}".format("Read_lines")
            print(series_id_formatted+"||"+rch_formatted+"||"+variable_formatted+"||"+obj_type_formatted+"||"+obj_id_formatted+"||"+weight_formatted+"||"+data_formatted)
            for obj_id, series in obj_comb.items():
                for id in series:
                    i=id-1
                    series_id_formatted="{:^10}".format(id)
                    rch_formatted="{:^10}".format(data_infos[i][1])
                    variable_formatted= "{:^10}".format(VARNAME[data_infos[i][2]])
                    obj_type_formatted= "{:^10}".format(OBJ_TYPE_NAME[data_infos[i][3]])
                    obj_id_formatted= "{:^10}".format(data_infos[i][4])
                    weight_formatted= "{:^10}".format(data_infos[i][5])
                    lines=data_infos[i][6]
                    line_str=""
                    for line in lines:
                        line_str+=str(line[0])+"-"+str(line[1])+" "
                    data_formatted= "{:<30}".format(line_str)
                    print(series_id_formatted+"||"+rch_formatted+"||"+variable_formatted+"||"+obj_type_formatted+"||"+obj_id_formatted+"||"+weight_formatted+"||"+data_formatted)
            print("="*70)
            
    def _get_lines_for_output(self, index):
        
        index.ravel().sort()
        cur_group=[index[0]]; lines_group=[]
        
        for i in range(1, len(index)):
            if index[i]==cur_group[-1]+1:
                cur_group.append(index[i])
            else:
                lines_group+=self._generate_data_lines(cur_group)
                cur_group=[index[i]]
        
        lines_group+=self._generate_data_lines(cur_group)
        
        return lines_group
    
    def _generate_data_lines(self, group):
        
        start=group[0];end=group[-1]
        print_flag=self.model["print_flag"]
        n_rch=self.model["n_rch"]

        lines=[]
        if print_flag==0:
            begin_month=self.model["begin_record"].month
            first_period=12-begin_month
            if start<=first_period:
                if end<=first_period:
                    end_in_year=end
                    lines.append([10+n_rch*start, 9+n_rch*(end_in_year+1)])
                    return lines
                else:
                    end_in_year=first_period
                lines.append([10+n_rch*start, 9+n_rch*(end_in_year+1)])
            else:
                years=start//12
                start_in_year=start
                end_in_year=years*12+11
                if end<end_in_year:
                    lines.append([10+n_rch*start_in_year+n_rch*years, 9+n_rch*(end+1)+n_rch*years])
                    return lines
                else:
                    lines.append([10+n_rch*start_in_year, 9+n_rch*(end_in_year+1)+n_rch*years])
            while True:
                start_in_year=end_in_year+1
                end_in_year=start_in_year+11
                years=(start_in_year-first_period)//12+1
                if end_in_year>=end:
                    lines.append([10+n_rch*start_in_year+n_rch*years, 9+n_rch*(end+1)+n_rch*years])
                    break
                else:
                    lines.append([10+n_rch*start_in_year, 9+n_rch*(end_in_year+1)+n_rch*years])
            return lines 
        elif print_flag==1:
            lines=[[10+n_rch*start, 9+n_rch*(end+1)]]
            return lines
            
    def _record_default_values(self):
        """
        record default values from the swat file
        """
        
        var_infos_path=os.path.join(self.work_path, self.paraInfos_name)
        low_bound=[]
        up_bound=[]
        disc_var=[]
        var_name=[]
        mode=[]
        assign_hru_id=[]
        discrete_bound=[]
        with open(var_infos_path, 'r') as f:
            lines=f.readlines()
            for line in lines:
                tmp_list=line.split()
                var_name.append(tmp_list[0])
                mode.append(tmp_list[1])
                op_type=tmp_list[2]
                lower_upper=tmp_list[3].split("_")
                
                if op_type=="c":
                    low_bound.append(float(lower_upper[0]))
                    up_bound.append(float(lower_upper[1]))
                    discrete_bound.append(0)
                    disc_var.append(0)
                else:
                    low_bound.append(float(lower_upper[0]))
                    up_bound.append(float(lower_upper[-1]))
                    discrete_bound.append([float(e) for e in lower_upper])
                    disc_var.append(1)
                    
                assign_hru_id.append(tmp_list[4:])
                
        if self.verboseFlag:
            print("="*50+"Parameter Information"+"="*50)
            name_formatted="{:^20}".format("Parameter name")
            type_formatted="{:^7}".format("Type")
            mode_formatted= "{:^7}".format("Mode")
            low_bound_formatted="{:^15}".format("Lower bound")
            up_bound_formatted="{:^15}".format("Upper bound")
            assign_hru_id_formatted="{:^20}".format("HRU ID or Sub_HRU ID")
            print(name_formatted+"||"+type_formatted+"||"+mode_formatted+"||"+low_bound_formatted+"||"+up_bound_formatted+"||"+assign_hru_id_formatted)
            for i in range(len(var_name)):
                name_formatted="{:^20}".format(var_name[i])
                type_formatted="{:^7}".format("Float" if disc_var[i]==0 else "int")
                mode_formatted= "{:^7}".format(mode[i])
                low_bound_formatted="{:^15}".format(low_bound[i])
                up_bound_formatted="{:^15}".format(up_bound[i])
                assign_hru_id_formatted="{:^20}".format(" ".join(assign_hru_id[i]))
                print(name_formatted+"||"+type_formatted+"||"+mode_formatted+"||"+low_bound_formatted+"||"+up_bound_formatted+"||"+assign_hru_id_formatted)
            print("="*120)
            print("\n"*1)
            
        file_var_info={}
        
        # self.data_types=[]
        watershed_hru=self.model["watershed_hru"]
        watershed_list=self.model["watershed_list"]
        hru_list=self.model["hru_list"]
        for i, element in enumerate(var_name):
            element=element.split('@')[0]
            suffix=self.paraInfos.query('para_name==@element')['file_name'].values[0]
            position=self.paraInfos.query('para_name==@element')['position'].values[0]
            
            if(self.paraInfos.query('para_name==@element')['type'].values[0]=="int"):
                data_type_=0
            else:
                data_type_=1
            # self.data_types.append(data_type_)
            if suffix in HRU_SUFFIX:
                if assign_hru_id[i][0]=="all":
                    files=[e+".{}".format(suffix) for e in hru_list]
                else:
                    files=[]
                    for ele in assign_hru_id[i]:
                        if "_" not in ele:
                            code=f"{'0' * (9 - 4 - len(ele))}{ele}{'0'*4}"
                            for e in watershed_hru[code]:
                                files.append(e+"."+suffix)
                        else:
                            hru_id, bsn_id=ele.split('_')
                            code=f"{'0' * (9 - 4 - len(bsn_id))}{bsn_id}{'0'*(4-len(hru_id))}{bsn_id}"
                            files.append(code+"."+suffix)
            elif suffix in WATERSHED_SUFFIX:
                if assign_hru_id[i][0]=="all":
                    files=[e+"."+suffix for e in watershed_list]
                else:
                    files=[e+"."+suffix for e in assign_hru_id[i]]
            elif suffix=="bsn":
                files=["basins.bsn"]
            
            for file in files:
                file_var_info.setdefault(file,{})
                file_var_info[file].setdefault("index", [])
                file_var_info[file]["index"].append(i)
                file_var_info[file].setdefault("mode", [])
                if mode[i]=="v":
                    file_var_info[file]["mode"].append(0)
                elif mode[i]=="r":
                    file_var_info[file]["mode"].append(1)
                elif mode[i]=="a":
                    file_var_info[file]["mode"].append(2)
                
                file_var_info[file].setdefault("name", [])
                file_var_info[file]["name"].append(element)
                file_var_info[file].setdefault("position",[])
                file_var_info[file]["position"].append(position)
                file_var_info[file].setdefault("type", [])
                file_var_info[file]["type"].append(data_type_)
                                
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            
            futures=[]
            for file_name, infos in file_var_info.items():
                futures.append(executor.submit(read_value_swat, self.work_path, file_name , infos["name"], infos["position"], 1))

        for future in futures:
            res=future.result()
            for key, items in res.items():
                values=' '.join(str(value) for value in items)
                _, file_name=key.split('|')
                file_var_info[file_name].setdefault("default", [])
                file_var_info[file_name]["default"].append(values)
        
        #model setting
        self.model['mode']=mode
        self.model['paras_list']=var_name
        self.model['file_var_info']=file_var_info
        
        #problem setting
        self.lb= np.array(low_bound).reshape(1,-1)
        self.ub= np.array(up_bound).reshape(1,-1)
        self.x_labels=var_name
        self.disc_range=discrete_bound
        self.disc_var=disc_var
        self.nInput=len(var_name)
        
    def delete(self):
        shutil.rmtree(self.work_temp_dir)

