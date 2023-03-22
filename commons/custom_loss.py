def ge_loss(y_true, y_pred):
        import numpy as np
        import random
        import tensorflow as tf
        from sklearn.utils import shuffle

        from commons.datasets import SCADatasets
        from commons.load_datasets import LoadDatasets

        def aes_labelize_ge_sr(trace_data, byte, key, leakage):
                    
            AES_Sbox = np.array([
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16])
            
            pt_ct = [row[byte] for row in trace_data]

            key_byte = np.full(len(pt_ct), key[byte])
            state = [int(x) ^ int(k) for x, k in zip(np.asarray(pt_ct[:]), key_byte)]

            intermediate_values = AES_Sbox[state]

            if leakage == "HW":
                return [bin(iv).count("1") for iv in intermediate_values]
            else:
                return intermediate_values

        byte=2
        l_model="HW"
        param = SCADatasets().get_trace_set("ascad_fixed_key")
        
        print("Before load database")
        root_folder = "/home/yiy003/private/ECE268/EnsembleSCA/ASCAD/ATMEGA_AES_v1/ATM_AES_v1_fixed_key/ASCAD_data/ASCAD_databases/"

        (X_profiling, Y_profiling), (X_validation, Y_validation), (X_attack, Y_attack), (
            _, plt_validation, plt_attack) = LoadDatasets().load_dataset(
            root_folder + param["file"], param["n_profiling"], param["n_attack"], byte, l_model)
        
        print("After load database")
        output_probabilities = y_pred.numpy()
        print(output_probabilities.shape)

        test_trace_data = plt_validation[:400]
        print(f'X_profiling {len(X_profiling)}')
        print(f'plt_validation {len(plt_validation)}')

        print("After test_trace_data")
        nt = 400
        step=10
        runs=100
        fraction=1
        nt_kr = int(nt / fraction)
        nt_interval = int(nt / (step * fraction))
        key_ranking_sum = np.zeros(nt_interval)
        key_probabilities_key_ranks = np.zeros((runs, nt, 256))

        print("Before labels")
        labels_key_hypothesis = np.zeros((256, nt))
        for key_byte_hypothesis in range(0, 256):
            key_h = bytearray.fromhex(param["key"])
            key_h[byte] = key_byte_hypothesis
            labels_key_hypothesis[key_byte_hypothesis][:] = aes_labelize_ge_sr(test_trace_data, byte, key_h, l_model)
            print("After aes_labelize_ge_sr")
        
        print("After labels")
        probabilities_kg_all_traces = np.zeros((nt, 256))
        
        
        print("Before probabilities_kg_all_traces")
        print(len(output_probabilities[0][np.asarray([int(leakage[0]) for leakage in labels_key_hypothesis[:]])]))
        print(output_probabilities.shape)
        print(len(np.asarray([int(leakage[0]) for leakage in labels_key_hypothesis[:]])))
        print(len(labels_key_hypothesis[:]))
        for index in range(nt):
            probabilities_kg_all_traces[index] = output_probabilities[index][
                    np.asarray([int(leakage[index]) for leakage in labels_key_hypothesis[:]])
                ]
        
        print(probabilities_kg_all_traces)

        print("After probabilities_kg_all_traces")
        
        print("Before run loop")
        for run in range(runs):
            probabilities_kg_all_traces_shuffled = shuffle(probabilities_kg_all_traces, random_state=random.randint(0, 100000))
            key_probabilities = np.zeros(256)
            kr_count = 0
            for index in range(nt_kr):
                key_probabilities += np.log(probabilities_kg_all_traces_shuffled[index] + 1e-36)
                key_probabilities_key_ranks[run][index] = probabilities_kg_all_traces_shuffled[index]
                key_probabilities_sorted = np.argsort(key_probabilities)[::-1]
                if (index + 1) % step == 0:
                    key_ranking_good_key = list(key_probabilities_sorted).index(param["good_key"]) + 1
                    key_ranking_sum[kr_count] += key_ranking_good_key
                    kr_count += 1
            print(
                "KR: {} | GE for correct key ({}): {})".format(run, param["good_key"], key_ranking_sum[nt_interval - 1] / (run + 1)))
            print(key_ranking_sum[nt_interval - 1])
        
        print("After run loop")
        guessing_entropy = key_ranking_sum / runs
        print(key_ranking_sum)
        
        print("Before return")
        print(guessing_entropy[-1])
        return guessing_entropy[-1]


       