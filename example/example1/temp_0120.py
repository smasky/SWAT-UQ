import sys
sys.path.append(".")


from swatuq import createFileHandler, set_value_FileHandler

var_list = [0, 1]

mode_list = [0, 1]

type_list = [0, 0]

linePos_list = [11, 17]

staPos_list = [28, 28]

endPos_list = [39, 39]

precision_list = [2, 2]

colStep_list = [12, 12]

maxCols_list = [15, 15]

handler = createFileHandler(
        "./example/example1/000330012.sol", 
        var_list, 
        mode_list, 
        type_list, 
        linePos_list, 
        staPos_list, 
        endPos_list, 
        precision_list, 
        colStep_list, 
        maxCols_list
    )

new_values = [0.10, 2.00]
target_layers = [1, 1]

set_value_FileHandler(
        handler, 
        "./example/example1/000330012_new.sol", 
        var_list, 
        new_values, 
        target_layers
    )



 

