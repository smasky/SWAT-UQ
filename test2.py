import h5py

# 打开 HDF5 文件
def h5_to_dict(h5_obj):
    """
    将 HDF5 文件或组转换为字典。
    """
    result = {}
    for key, item in h5_obj.items():
        if isinstance(item, h5py.Dataset):
            # 如果是数据集，直接读取数据
            result[key] = item[()]
        elif isinstance(item, h5py.Group):
            # 如果是组，递归调用
            result[key] = h5_to_dict(item)
    return result

with h5py.File('./Result/Data/RBD_FAST_None_1.hdf', 'r') as file:
    # 列出所有组
    print("Keys: %s" % file.keys())
    # 获取某个数据集
    data_dict = h5_to_dict(file)
    a=1
    