import numpy as np
import subprocess
import os

def SAEConv_simulation(Conv_name,Conv_title, InputValueIn, ConvValuePIn, ConvValueNIn, ConvStride,ConvBiasPIn, ConvBiasNIn,ConvBiasVoltage):
    all_results = []
    if ConvBiasPIn is not None:
        circuit_input_number = InputValueIn.shape[0]
        circuit_output_number = ConvValuePIn.shape[0]
        flattenedInput = InputValueIn.flatten()
        ConvValuePIn= ConvValuePIn.flatten()
        ConvValueNIn = ConvValueNIn.flatten()
        ConvBiasPIn = ConvBiasPIn.flatten()
        ConvBiasNIn = ConvBiasNIn.flatten()
        output_directory = 'output_files/'
        file_name = f'{Conv_name}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Conv_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F\n")
            cir_file.write(f"VB b 0 {ConvBiasVoltage}\n")
            NConvBiasVoltage = -ConvBiasVoltage
            cir_file.write(f"VNB nb 0 {NConvBiasVoltage}\n")
            for index, voltage in enumerate(flattenedInput, start=1):
                cir_file.write(f"VQ{index} QInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(flattenedInput, start=1):
                voltage = -voltage
                cir_file.write(f"VW{index} WInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, value in enumerate(ConvValuePIn):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NQ{index + 1} QInput{index % circuit_input_number + 1} QVMMOut{index // circuit_input_number + 1} HP wic={formatted_value}\n")
            cir_file.write("\n")
            for index, wic_values in enumerate(ConvBiasPIn):
                cir_file.write(f"NQB{index + 1} b QVMMOut{index + 1} HP wic={wic_values}\n")
            cir_file.write("\n")
            for index, value in enumerate(ConvValueNIn):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NQN{index + 1} WInput{index % circuit_input_number + 1} QVMMOut{index // circuit_input_number + 1} HP wic={formatted_value}\n")
            cir_file.write("\n")
            for index, wic_values in enumerate(ConvBiasNIn):
                    if (formatted_value != '999999936.0000000000'):
                        cir_file.write(f"NQBN{index + 1} nb QVMMOut{index + 1} HP wic={wic_values}\n")
            cir_file.write("\n")
            for index in range(circuit_output_number):
                cir_file.write(f" VT{index + 1} QVMMOut{index + 1} 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(circuit_output_number):
                cir_file.write(f" print I(VT{index + 1})\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")

        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Conv_name}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('i(vt'):
                parts = line.split('=')
                value_str = parts[1].strip()
                try:
                    value = float(value_str)
                    current_values.append(value)
                except ValueError:
                    print(f"Error parsing value: {value_str}")
        all_results.append(current_values)
        matrix = np.array(all_results)
        result_matrix = matrix.reshape((matrix.shape[1], 1, 1))
        return result_matrix
    else:
        circuit_input_number = InputValueIn.shape[0]
        circuit_output_number = ConvValuePIn.shape[0]
        flattenedInput = InputValueIn.flatten()
        ConvValuePIn = ConvValuePIn.flatten()
        ConvValueNIn = ConvValueNIn.flatten()
        output_directory = 'output_files/'
        file_name = f'{Conv_name}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Conv_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F\n")
            for index, voltage in enumerate(flattenedInput, start=1):
                cir_file.write(f"VQ{index} QInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(flattenedInput, start=1):
                voltage = -voltage
                cir_file.write(f"VW{index} WInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, value in enumerate(ConvValuePIn):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NQ{index + 1} QInput{index % circuit_input_number + 1} QVMMOut{index // circuit_input_number + 1} HP wic={formatted_value}\n")
            cir_file.write("\n")
            for index, value in enumerate(ConvValueNIn):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NQN{index + 1} WInput{index % circuit_input_number + 1} QVMMOut{index // circuit_input_number + 1} HP wic={formatted_value}\n")
            cir_file.write("\n")

            for index in range(circuit_output_number):
                cir_file.write(f" VT{index + 1} QVMMOut{index + 1} 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(circuit_output_number):
                cir_file.write(f" print I(VT{index + 1})\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Conv_name}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('i(vt'):
                parts = line.split('=')
                value_str = parts[1].strip()
                try:
                    value = float(value_str)
                    current_values.append(value)
                except ValueError:
                    print(f"Error parsing value: {value_str}")
        all_results.append(current_values)
        matrix = np.array(all_results)
        # result_matrix = matrix.reshape((matrix.shape[1], 1, 1))
        return matrix
