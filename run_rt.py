import os

# Constants for sub-directories
MAKE_CELLDATA_DIR = './MakeCelldata'


def get_default_params():
    """
    :return: A dicitonary containing the default values of
    all parameters
    """
    return {
        'output_dir': '~/lya_igm_rt/',
        'velocity_file': None,
        'density_file': None,
        'xfrac_file': None,
        'redshift': None
    }


def write_make_celldata_config(params_dict):
    """
    Write the settings.txt file used by make_celldata

    :param params_dict: Dictionary containing the parameters
    """
    filename = os.path.join(MAKE_CELLDATA_DIR, 'settings.txt')
    output_filename = os.path.join(params_dict['output_dir'], 'CellData.bin')
    with open(filename, 'w') as f:
        f.write('&settings\n')
        f.write('vfile=\'%s\'' % params_dict['velocity_file'])
        f.write('dfile=\'%s\'' % params_dict['density_file'])
        f.write('xfile=\'%s\'' % params_dict['xfrac_file'])
        f.write('outfile=\'%s\n' % output_filename)
        f.write('redshift=%.3f\n' % params_dict['redshift'])
        f.write('/')
