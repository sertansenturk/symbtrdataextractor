import os


class MusicXMLReader(object):
    def __init__(self):
        """
        Class constructor
        """
        pass

    @classmethod
    def read(cls, score_file, symbtr_name=None):
        """
        Reader method for the SymbTr-MusicXML scores. This method is not
        implemented yet.

        Parameters
        ----------
        score_file : str
            The path of the SymbTr score
        symbtr_name : str, optional
            The name of the score in SymbTr naming convention
            (makam--form--usul--name--composer).
        Returns
        ----------
        NotImplemented
        """
        if symbtr_name is None:
            symbtr_name = os.path.splitext(os.path.basename(score_file))[0]

        # TODO
        return NotImplemented