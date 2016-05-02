import numpy as np


def write_galdata(halo_data, filename):
    """
    Write the final galdata file from a
    dictionary containing properties about halos

    :param halo_data: Dictionary containing halo properties.
    The following properties must be present:
    x_pos_kpc
    y_pos_kpc
    z_pos_kpc
    rvir_kpc
    x_vel_kms (corrected for Hubble flow)
    y_vel_kms
    z_vel_kms
    logMsol
    :param filename: The name of the output file
    """
    output_keys =['x_pos_kpc', 'y_pos_kpc', 'z_pos_kpc', 'rvir_kpc',
                  'x_vel_kms', 'y_vel_kms', 'z_vel_kms', 'logMsol']
    n_halos = len(halo_data['x_pos_kpc'])
    with open(filename, 'w') as f:
        f.write('# x \t y \t z \t r_vir \t v_x \t v_y \t v_z \t log10(M) \n')
        f.write('#----------------------------------------------------------------------\n')
        f.write('#kpc \t kpc \t kpc \t kpc \t km/s \t km/s \t km/s \t log10(solar mass)\n')
        f.write('#----------------------------------------------------------------------\n')
        for i in xrange(n_halos):
            l = ' \t '.join([str(halo_data[k][i]) for k in output_keys])
            f.write(l + '\n')


def test_run(output_file):
    halo_test = dict(
       x_pos_kpc=np.array([1.0, 1.2, -1.0]),
       y_pos_kpc=np.array([2.0, -1.3, -5.0]),
       z_pos_kpc=np.array([-5.0, 1.3, -1.7]),
       rvir_kpc=np.array([13., 14., 15.]),
       x_vel_kms=np.array([10., 12., -10.]),
       y_vel_kms=np.array([20., -13., -50.]),
       z_vel_kms=np.array([-50., 1., -17.]),
       logMsol=np.array([11., 12.5, 10.7])
    )
    write_galdata(halo_test, output_file)

