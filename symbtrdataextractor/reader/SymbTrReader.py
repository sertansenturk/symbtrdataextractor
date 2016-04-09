import os


class SymbTrReader(object):
    @staticmethod
    def get_symbtr_name_from_filepath(score_file, symbtr_name):
        return os.path.splitext(os.path.basename(score_file))[0]
