import os
import subprocess
import shutil

# Constants for sub-directories
MAKE_CELLDATA_DIR = './MakeCelldata'
SIMPLETRANSFER_DIR = './SimpleTransfer'


def get_default_params():
    """
    :return: A dicitonary containing the default values of
    all parameters
    """
    return dict(output_dir='~/lya_igm_rt/',
                velocity_file='velocity.bin',
                density_file='density.bin',
                xfrac_file='xfrac.bin',
                redshift=7.,
                raw_output='transmission_out.bin',
                start_dist_vr=1.5,
                specres_bins=1500,
                wavel_lower=1180.,
                wavel_upper=1220.,
                num_los=1,
                num_sightlines_between_writes=10000,
                frac_total_radius=2.,
                hubble_const=70.,
                omega_m=0.27,
                omega_0=0.73,
                los_dir='x',
                n_box=10976,
                boxsize=425.,
                overwrite_output=False
                )


def prepare_output_dir(params_dict):
    """
    Create output dir if it does not
    exist. If overwrite_output is true,
    delete everything in it.

    :param params_dict: Dictionary containing parameters
    """
    if not os.path.exists(params_dict['output_dir']):
        print 'Output dir does not exist. Creating.'
        os.mkdir(params_dict['output_dir'])

    dir_is_empty = (os.listdir(params_dict['output_dir']) == [])
    if not dir_is_empty and params_dict['overwrite_output']:
        print 'Output dir is not empty, and overwrite is\
                set to true. Deleting contents'
        shutil.rmtree(params_dict['output_dir'])
        os.mkdir(params_dict['output_dir'])  # rmtree deletes the directory as well


def run_make_celldata(params_dict):
    """
    Run the make_celldata program after
    writing a temporary settings file

    :param params_dict: Dictionary containing parameters
    """
    write_make_celldata_config(params_dict)
    cwd = os.getcwd()
    os.chdir(MAKE_CELLDATA_DIR)
    print 'Running make_celldata'
    subprocess.call('./make_celldata.x')
    os.chdir(cwd)


def run_make_galdata(params_dict):
    pass


def run_simpletransfer(params_dict):
    pass


def run_full_pipeline(params_dict):
    pass


def read_params_from_file(params_file, add_defaults=True):
    """
    Read simulation paramers from a file and
    return them as a dictionary. Also check
    that all the required keys are present

    :param params_file: The file containing the parameters
    :param add_defaults: If true, fill in missing parameters with
    default values
    :return: A dictionary with the parameters
    """
    # Read parameters from the file
    params_dict = dict()
    with open(params_file, 'r') as f:
        for l in f.readlines():
            if '=' in l:
                l = l.split('#')[0].strip()
                k, v = l.split('=')
                params_dict[k.strip()] = v
    # Check if all keys are present
    default_params = get_default_params()
    for k in default_params.keys():
        if k not in params_dict.keys():
            print 'Warning! Key', k, 'not present in file'
            if add_defaults:
                print 'Adding default value'
                params_dict[k] = default_params[k]
    # Check if bad keys are present
    for k in params_dict.keys():
        if k not in default_params.keys():
            print 'Warning! Key', k, 'will be ignored'
    return params_dict


def write_make_celldata_config(params_dict):
    """
    Write the settings.txt file used by make_celldata

    :param params_dict: Dictionary containing the parameters
    """
    filename = os.path.join(MAKE_CELLDATA_DIR,
                            'make_cell_data_parameters.txt')
    output_filename = os.path.join(params_dict['output_dir'], 'CellData.bin')
    output = [
        '&settings',
        'vfile=\'%s\'' % params_dict['velocity_file'],
        'dfile=\'%s\'' % params_dict['density_file'],
        'xfile=\'%s\'' % params_dict['xfrac_file'],
        'outfile=\'%s' % output_filename,
        'redshift=%.3f' % params_dict['redshift'],
        'n_box=%d' % params_dict['n_box'],
        'boxsize=%f' % params_dict['boxsize'],
        '/'
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(map(str, output)))


def write_simpletransfer_config(params_dict):
    """
    Write the setting fils for SimpleTransfer to read

    :param params_dict: Dictionary containing the parameters
    """
    filename = os.path.join(SIMPLETRANSFER_DIR, 'simpletransfer_settings.in')
    output = [
        params_dict['output_dir'],  # data_dir
        '',  # data_subdir
        'CellData.bin',  # celldata_file
        'GalData.dat',  # galdata_file
        params_dict['output_dir'],  # data_subdir_in
        params_dict['raw_output'],  # data_filename
        '',  # proc_file in old version. not used
        params_dict['redshift'],  # sim_z
        params_dict['start_dist_vr'],  # sim_distvr
        params_dict['specres_bins'],  # sim_res
        '%f %f' % (params_dict['wavel_lower'], params_dict['wavel_upper']),
        '%f %f' % (params_dict['wavel_lower'], params_dict['wavel_upper']),
        params_dict['num_los'], # sim_los
        params_dict['num_sightlines_between_writes'],
        params_dict['frac_total_radius'],
        params_dict['hubble_const'],
        params_dict['omega_m'],
        params_dict['omega_0'],
        params_dict['los_dir']
    ]
    with open(filename, 'w') as f:
        f.write('\n'.join(map(str, output)))


# -------------------- TEST -----------------------------
if __name__ == '__main__':
    params = read_params_from_file('sample_settings.txt')
    prepare_output_dir()
    run_make_celldata(params)
