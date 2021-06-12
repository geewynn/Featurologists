import socketserver
import subprocess
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from sklearn.preprocessing import LabelEncoder


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
        return free_port


def kubectl_port_forward(
    ns: str, what: str, port_remote: int
) -> Tuple[subprocess.Popen, int]:
    port_local = get_free_port()
    p = subprocess.Popen(
        [
            "kubectl",
            "-n",
            "feast-dev",
            "port-forward",
            what,
            f"{port_local}:{port_remote}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"pid: {p.pid}")
    try:
        n_sec = 2
        stdout, stderr = p.communicate(timeout=n_sec)
        raise ValueError(
            f"Port-forward process for {what} has terminated within "
            f"{n_sec} sec: stdout={str(stdout)}, stderr={str(stderr)}"
        )
    except subprocess.TimeoutExpired:
        print(
            f"Port-forward process for '{what}' seems to be working:"
            f"check 'localhost:{port_local}'"
        )

    return p, port_local


class LabelEncoderExt:
    # Source: https://stackoverflow.com/a/56876351/4977823

    def __init__(self):
        """
        It differs from LabelEncoder by handling new
        classes and providing a value for it [Unknown]
        Unknown will be added in fit and transform will
        take care of new item. It gives unknown class id
        """
        self.label_encoder = LabelEncoder()

    def fit(self, data_list):
        """
        This will fit the encoder for all the unique values
        and introduce unknown value
        :param data_list: A list of string
        :return: self
        """
        self.label_encoder = self.label_encoder.fit(list(data_list) + ["Unknown"])
        self.classes_ = self.label_encoder.classes_

        return self

    def transform(self, data_list):
        """
        This will transform the data_list to id list where the
        new values get assigned to Unknown class
        :param data_list:
        :return:
        """
        new_data_list = list(data_list)
        for unique_item in np.unique(data_list):
            if unique_item not in self.classes_:
                new_data_list = [
                    "Unknown" if x == unique_item else x for x in new_data_list
                ]

        return self.label_encoder.transform(new_data_list)

    @classmethod
    def load(cls, path: Union[Path, str]):
        encoder = cls()
        encoder.label_encoder.classes_ = np.load(path, allow_pickle=True)
        encoder.classes_ = encoder.label_encoder.classes_
        return encoder
