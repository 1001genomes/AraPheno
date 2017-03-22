from rest_framework.parsers import BaseParser
import csv

class AccessionTextParser(BaseParser):
    """
    Parser for accession ids
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Return a list of accesion ids
        """
        accession_ids = []
        body=stream.read()
        parts = body.splitlines()
        # check if comma
        if len(parts) == 1:
            parts = body.split(',')

        for accession_id in parts:
            accession_ids.append(int(accession_id))

        return accession_ids

