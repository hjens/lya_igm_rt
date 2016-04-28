import os

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
                boxsize=425.
                )


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
    params = get_default_params()
    write_make_celldata_config(params)
    write_simpletransfer_config(params)
