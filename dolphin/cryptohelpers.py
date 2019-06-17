import binascii
import hashlib
import os
import time

from oathcy import OCRAChallengeResponseServer, OCRAChallengeResponseClient


def random(size): # pragma: no cover
    return os.urandom(size)


hash_algorithm_sizes = {
    'SHA-1': 20,
    'SHA-256': 32,
    'SHA-384': 48,
    'SHA-512': 64,
}


def split_seed(seed, hash_algorithm): # pragma: no cover
    if not isinstance(seed, bytes):
        raise TypeError('seed argument must be bytes')

    return seed[:hash_algorithm_sizes[hash_algorithm]]


def derivate_seed(base_seed, second_factor): # pragma: no cover
    sha = hashlib.sha3_256()
    sha.update(second_factor.encode())
    hashed = sha.digest()
    result = bytearray(base_seed)
    for i, b in enumerate(hashed):
        result[i] ^= b
    return bytes(result)


class AbstractAlgorithm: # pragma: no cover
    def __init__(self, seed, drift=0):
        self.seed = seed
        self.drift = drift

    @property
    def hexlified_seed(self):
        return binascii.hexlify(self.seed).decode()

    def generate(self, *args, **kwargs):
        raise NotImplementedError()

    def verify(self, *args, **kwargs):
        raise NotImplementedError()


class OCRASuite: # pragma: no cover
    algorithm = 'OCRA-1'

    def __init__(self, counter_type, length, hash_algorithm,
                 time_interval=None, challenge_limit=40):
        """
        The OCRASuite V1:
        :param counter_type: 'time' or 'counter'
        :param length: 4-10
        :param time_interval: In seconds
        :param challenge_limit: 40 is a good value
        :return:
        """

        # We only support time OTP and counter OTP
        if counter_type not in ('time', 'counter'):
            raise ValueError('We only support time OTP and counter OTP')
        self.counter_type = counter_type

        if length < 4 or length > 10:
            raise ValueError('Length should be between 4-10')
        self.length = length

        if hash_algorithm not in ['SHA-1', 'SHA-256', 'SHA-384', 'SHA-512']:
            raise ValueError('This hash type does not supported')
        self.hash_algorithm = hash_algorithm

        if counter_type == 'time' and time_interval is None:
            raise ValueError('counter_type == time and not time_interval')
        self.time_interval = time_interval

        if challenge_limit < 4 or challenge_limit > 64:
            raise ValueError('Challenge limit value must be between 4-64')
        self.challenge_limit = challenge_limit

    def __str__(self):
        """
        Algorithm: CryptoFunction:DataInput
         [C] | QFxx | [PH | Snnn | TG] : Challenge-Response computation
         [C] | QFxx | [PH | TG] : Plain Signature computation
               +------------------+-------------------+
               |    Format (F)    | Up to Length (xx) |
               +------------------+-------------------+
               | A (alphanumeric) |       04-64       |
               | N (numeric)      |       04-64       |
               | H (hexadecimal)  |       04-64       |
               +------------------+-------------------+
         +--------------------+------------------------------+
         | Time-Step Size (G) |           Examples           |
         +--------------------+------------------------------+
         |       [1-59]S      | number of seconds, e.g., 20S |
         |       [1-59]M      | number of minutes, e.g., 5M  |
         |       [0-48]H      | number of hours, e.g., 24H   |
         +--------------------+------------------------------+
        Sample: OCRA - 1: HOTP - SHA1 - 6: QA40 - T1M
        """

        crypto_function = '-'.join([
            'HOTP',
            self.hash_algorithm.replace('-', ''),
            str(self.length)
        ])

        data_input = ''
        if self.counter_type == 'time':
            if self.time_interval == 0:
                raise ValueError('Time interval should not be zero')
            elif 60 <= self.time_interval <= 59 * 60 \
                    and self.time_interval % 60 != 0:
                raise ValueError(
                    '60 <= time_interval <= 59 * 60 and time_interval '
                    '% 60 != 0'
                )
            elif 60 * 60 <= self.time_interval <= (48 * 60 * 60) \
                    and self.time_interval % (60 * 60) != 0:
                raise ValueError(
                    '60 <= time_interval <= 59 * 60 and time_interval '
                    '% 60 != 0'
                )

            def format_time(t):
                if t >= 60:
                    t /= 60
                    if t > 60:
                        t /= 60
                        return t, 'H'
                    return t, 'M'
                return t, 'S'

            data_input = '-'.join(
                [
                    'QA%02d' % self.challenge_limit,
                    'T%d%s' % format_time(self.time_interval)
                ]
            )

        elif self.counter_type == 'counter':
            data_input = '-'.join(['C', 'QA%02d' % self.challenge_limit])

        return ':'.join([self.algorithm, crypto_function, data_input])

    @classmethod
    def load(cls, ocra_suite):
        ocra_suite_parts = ocra_suite.split(':')

        crypto_function = ocra_suite_parts[1]
        data_input = ocra_suite_parts[2]

        crypto_function_parts = crypto_function.split('-')
        hash_algorithm = f'SHA-{crypto_function_parts[1][3:]}'
        length = int(crypto_function_parts[2])

        time_interval = None

        data_input_parts = data_input.split('-')
        if data_input_parts[0] == 'C':
            counter_type = 'counter'
        else:
            counter_type = 'time'
            time_unit_coefficients = {'S': 1, 'M': 60, 'H': 3600}
            time_interval = \
                int(data_input_parts[1][1:-1]) \
                * time_unit_coefficients.get(data_input_parts[1][-1:])

        return cls(
            counter_type=counter_type,
            length=length,
            hash_algorithm=hash_algorithm,
            time_interval=time_interval,
        )


class ChallengeResponse(AbstractAlgorithm): # pragma: no cover
    def __init__(self, ocra_suite, seed, drift=0):
        if not isinstance(ocra_suite, OCRASuite):
            ocra_suite = OCRASuite.load(ocra_suite)
        self.ocra_suite = ocra_suite
        super().__init__(
            split_seed(seed, self.ocra_suite.hash_algorithm), drift=drift
        )

    def create_ocra_client(self):
        ocra_suite = str(self.ocra_suite)
        return OCRAChallengeResponseClient(
            self.seed,
            ocra_suite,
            ocra_suite
        )

    def create_ocra_server(self):
        ocra_suite = str(self.ocra_suite)
        return OCRAChallengeResponseServer(
            self.seed,
            ocra_suite,
            ocra_suite
        )


class MacBasedChallengeResponse(ChallengeResponse): # pragma: no cover
    def __init__(self, ocra_suite, seed, counter, drift=0):
        super().__init__(ocra_suite, seed, drift=drift)
        self.counter = counter

    def verify(self, code, challenge, window):
        backward_drift = min(window, self.counter) + self.drift
        for i in range(-backward_drift, self.drift + window + 1):
            ocra_server = self.create_ocra_server()
            kwargs = {'C': self.counter + i}
            ocra_server.compute_challenge()
            ocra_server.challenge = challenge
            if ocra_server.verify_response(response=code, **kwargs):
                return True, i

        return False, 0

    def generate(self, challenge):
        return self.create_ocra_client() \
            .compute_response(
                challenge=challenge,
                T=time.time(),
                T_precomputed='',
                C=self.counter
        )


class TimeBasedChallengeResponse(ChallengeResponse): # pragma: no cover
    def __init__(self, ocra_suite, seed, drift=0):
        super().__init__(ocra_suite, seed, drift=drift)
        self.time_interval = self.ocra_suite.time_interval

    def verify(self, code, challenge, window):
        for i in range(
                max(-divmod(time.time(), self.time_interval)[0], -window),
                window + 1
        ):
            d = (self.drift + i) * self.time_interval
            # for i in range(window_size + 1):
            ocra_server = self.create_ocra_server()
            ocra_server.compute_challenge()
            ocra_server.challenge = challenge
            if ocra_server.verify_response(
                    response=code,
                    T=time.time() + d,
                    T_precomputed=None
            ):
                return True, self.drift + i

        return False, 0

    def generate(self, challenge, time_=None):
        return self.create_ocra_client() \
            .compute_response(
                challenge=challenge,
                T=time_ if time_ else time.time(),
                T_precomputed=None
            )

