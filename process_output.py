import numpy as np
import struct
import spectrum_models as sm


def get_good_n_chunks(n_los, nmax=1000, nmin=1):
    """
    Find a suitable integer that divides n_los
    into an integer number of chunks
    """
    for n in range(nmax, nmin, -1):
        if np.mod(n_los, n) == 0:
            return n
    raise ValueError('Could not find a suitable n_chunks')


def process_output(transmissions_file, line_model, params_dict,
                   n_chunks=None):
    """
    Process the transmission functions in the given output
    file and calculate the transmitted fraction given the
    supplied line model

    :param transmissions_file: The filename containing the transmissions
    :param line_model: Callable that gives the line flux as a function
    of wavelength in Angstrom
    :param params_dict: Dictionary containing parameters
    :param n_chunks: The number of chunks to use when reading
    the file. If None, try to find a suitable value
    :return: Array with the transmitted fractions

    TODO: add halo masses parameters
    """
    # Extract info from parameters
    specres = params_dict['specres_bins']
    wavel = np.linspace(params_dict['wavel_lower'],
                        params_dict['wavel_upper'], specres)

    # Helper function
    def read_int(f):
        return struct.unpack('i', f.read(4))[0]

    # The output files can be very large, and need to be read in chunks
    fractions_out = []
    with open(transmissions_file, 'rb') as f:
        # Read header
        _ = read_int(f)  # FORTRAN record separator
        n_rec = read_int(f)
        n_los = read_int(f)
        _ = read_int(f)
        _ = read_int(f)

        # Find the number of chunks to use when reading the file
        if n_chunks is None:
            n_chunks = get_good_n_chunks(n_los=n_los)

        ifrac = n_los/n_rec
        recsize = ifrac*specres
        chunk_size = recsize/n_chunks
        assert np.mod(chunk_size, specres) == 0
        assert n_rec == 1

        # Read each record
        los_idx = 0
        for chunk in range(n_chunks):
            print 'Reading chunk ', chunk, ' of ', n_chunks
            tau = np.fromfile(f, dtype='float32', count=chunk_size)
            tau[tau != tau] = 1e10  # Try to prevent numerical problems
            tau[tau < 0] = 0.
            tau = tau.reshape((chunk_size/specres, specres))
            trans_func = np.exp(-tau)
            for i in range(trans_func.shape[0]):
                halo_idx = los_idx/n_los
                # TODO: replace with proper halo mass
                # TODO: replaceable line function
                spectrum_gmg = sm.get_line_double_gaussian(mass=10.,
                                                           wavel=wavel)

                trans_frac = sm.get_transmitted_fraction(spectrum_gmg,
                                                         trans_func[i, :],

                fractions_out.append(trans_frac)
                los_idx += 1

        return np.array(fractions_out)


if __name__ == '__main__':
    import run_rt
    params = run_rt.get_default_params()
    fractions = process_output('sample_transmission.bin', params_dict=params,
                               line_model=None)
    print fractions
