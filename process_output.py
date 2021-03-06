import numpy as np
import struct
import spectrum_models as sm


# Helper functions
def get_good_n_chunks(n_los, nmax=1000, nmin=1):
    """
    Find a suitable integer that divides n_los
    into an integer number of chunks
    """
    for n in range(nmax, nmin, -1):
        if np.mod(n_los, n) == 0:
            return n
    raise ValueError('Could not find a suitable n_chunks')


def read_int(f):
    return struct.unpack('i', f.read(4))[0]


def get_trans_frac_in_chunks(transmissions_file, line_model,
                             halo_masses, params_dict,
                             n_chunks=None, line_model_args={}):
    """
    Process the transmission functions in the given output
    file and calculate the transmitted fraction given the
    supplied line model

    :param transmissions_file: The filename containing the transmissions
    :param line_model: Callable that gives the line flux as a function
    of wavelength in Angstrom. This function must also accept a
    kwargs dict with additional parameters. One parameter will
    always be called 'mass', and contain the halo mass,
    log(Mh/Ms)
    :param halo_masses: Array containing the masses of each
    halo
    :param params_dict: Dictionary containing parameters
    :param n_chunks: The number of chunks to use when reading
    the file. If None, try to find a suitable value
    :param line_model_args: Dictionary containing extra arguments
    for the line model function. The halo mass will be automatically
    added
    :return: Array with the transmitted fractions

    """
    # Extract info from parameters
    specres = params_dict['specres_bins']
    wavel = np.linspace(params_dict['wavel_lower'],
                        params_dict['wavel_upper'], specres)

    # The output files can be very large, and need to be read in chunks
    fractions_out = []
    with open(transmissions_file, 'rb') as f:
        record_size, n_records, n_los = read_transmissions_header(f, specres)

        # Find the number of chunks to use when reading the file
        if n_chunks is None:
            n_chunks = get_good_n_chunks(n_los=n_los)

        chunk_size = record_size/n_chunks
        assert np.mod(chunk_size, specres) == 0
        assert n_records == 1

        # Read each record
        los_idx = 0
        for chunk in range(n_chunks):
            print 'Reading chunk ', chunk, ' of ', n_chunks
            tau = np.fromfile(f, dtype='float32', count=chunk_size)
            tau[tau != tau] = 1e10  # Try to prevent numerical problems
            tau[tau < 0] = 0.
            tau = tau.reshape((chunk_size/specres, specres))
            trans_func = np.exp(-tau)
            for i in xrange(trans_func.shape[0]):
                line_model_args['mass'] = \
                    halo_masses[float(los_idx)/n_los*len(halo_masses)]
                intrinsic_spectrum = line_model(wavel, **line_model_args)

                trans_frac = sm.get_transmitted_fraction(intrinsic_spectrum,
                                                         trans_func[i, :],
                                                         wavel)
                fractions_out.append(trans_frac)
                los_idx += 1

        return np.array(fractions_out)


def get_tau(transmissions_file, params_dict):
    """
    Read a raw output file from SimpleTransfer and
    return a matrix with dimensions (n_los, n_spec_bins)
    containing the optical depth as a function of wavelength

    The transmission function is related to tau as:
    T = exp(-tau)

    :param transmissions_file: The name of the file to read
    :param params_dict: Dictionary containing paramters
    :return: (wavel, tau) tuple. tau is a matrix containing
    the optical depth. It has dimensions (n_los, n_spec_bins)
    """

    # Extract info from parameters
    specres = params_dict['specres_bins']
    wavel = np.linspace(params_dict['wavel_lower'],
                        params_dict['wavel_upper'], specres)
    with open(transmissions_file, 'rb') as f:
        record_size, n_records, n_los = read_transmissions_header(f, specres)

        tau = np.zeros(n_los*specres, dtype='float32')
        for i in range(n_records):
            _ = read_int(f)  # FORTRAN record separators
            if i < n_records-1:
                tau[i*record_size:(i+1)*record_size] = np.fromfile(f, dtype='float32',
                                                                   count=record_size)
            else:
                tau[i*record_size:] = np.fromfile(f, dtype='float32',
                                                  count=n_los*specres-i*record_size)
            _ = read_int(f)
    tau[tau != tau] = 1e10  # Try to prevent numerical problems
    tau[tau < 0] = 0.

    tau = tau.reshape((n_los, specres))
    return wavel, tau


def read_transmissions_header(f, specres):
    """
    Read the header of a transmissions file

    :param f: File object
    :param specres: Spectral resolution
    :return: recsize, n_records, n_los
    """
    # Read the FORTRAN record separator
    _ = read_int(f)
    n_records = read_int(f)
    n_los = read_int(f)
    _ = read_int(f)

    ifrac = n_los/n_records
    recsize = ifrac*specres
    return recsize, n_records, n_los
