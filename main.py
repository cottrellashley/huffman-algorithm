import json
import heapq


class HuffmanNode:

    def __init__(self, weight, symbol: str = None):
        self.symbol = symbol
        self.weight = weight
        self.parent = None
        self.p_pointer: str = ""
        self.left = None
        self.right = None

    @property
    def is_leaf(self):
        return self.left is None and self.right is None

    @property
    def is_root(self):
        return self.parent is None

    def __lt__(self, other):
        return self.weight < other.weight

    def __eq__(self, other):
        return self.weight == other.weight

    def __add__(self, other):
        if isinstance(other, HuffmanNode):
            parent = HuffmanNode(weight=self.weight + other.weight)
            self.p_pointer = "0"
            other.p_pointer = "1"
            self.parent = parent
            other.parent = parent
            parent.left = self
            parent.right = other
            return parent

    # Existing code...
    def increment_weight(self):
        self.weight += 1

    @property
    def code(self):
        if not self.is_leaf:
            return None
        code = ""
        node = self
        while node.parent:
            code = code + node.p_pointer
            node = node.parent
        return code[::-1]


class HuffmanTree(dict):

    def __init__(self):
        super().__init__()
        self.original_data = None
        self.encoded_data = None

    def __missing__(self, symbol):
        self[symbol] = HuffmanNode(0, symbol)
        return self[symbol]

    def huffman_decode(self):
        # Step a: Reverse the Huffman codes
        reverse_codes = {v: k for k, v in self.codes.items()}
        data = self.encoded_data
        # Step b: Decoding
        current_code = ""
        decoded_data = ""
        for bit in data:
            current_code += bit
            if current_code in reverse_codes:
                decoded_data += reverse_codes[current_code]
                current_code = ""

        return decoded_data

    @classmethod
    def compress_string(cls, data: str):
        d = cls()
        d.original_data = data
        for char in data:
            d[char].increment_weight()

        heap = [n for c, n in d.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            parent = lo + hi
            heapq.heappush(heap, parent)
        d.encoded_data = "".join(d[symbol].code for symbol in d.original_data)
        return d

    @property
    def codes(self):
        return {k: v.code for k, v in self.items()}

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        return cls.compress_string(data)

    def save_to_file(self, data_file: str, metadata_file: str):
        # Save encoded data with a simple encoding map
        encoded_info = {
            'encoded_data_location': data_file,
            'huffman_tree': self.serialize_tree(),
            'original_length': len(self.original_data)
        }
        with open(metadata_file, 'w', encoding='utf-8') as file:
            json.dump(encoded_info, file)

        self.write_binary_data(data_file, self.encoded_data)

    def write_binary_data(self, filename: str, binary_string: str):
        byte_array = bytearray()

        for i in range(0, len(binary_string), 8):
            byte = int(binary_string[i:i + 8], 2)
            byte_array.append(byte)

        with open(filename, 'wb') as file:
            file.write(byte_array)

    def serialize_tree(self):
        return [(symbol, node.code) for symbol, node in self.items() if node.is_leaf]

    @classmethod
    def decode_from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            encoded_info = json.load(file)

        huffman_tree = cls()
        for symbol, code in encoded_info['huffman_tree']:
            current_node = huffman_tree.tree_root if huffman_tree.tree_root else HuffmanNode(0)
            for char in code:
                if char == '0':
                    if not current_node.left:
                        current_node.left = HuffmanNode(0)
                    current_node = current_node.left
                elif char == '1':
                    if not current_node.right:
                        current_node.right = HuffmanNode(0)
                    current_node = current_node.right
            current_node.symbol = symbol
            if not huffman_tree.tree_root:
                huffman_tree.tree_root = current_node

        # Set encoded data and decode
        huffman_tree.encoded_data = encoded_info['encoded_data']
        return huffman_tree.huffman_decode()


data_file_path = '/Users/ashleycottrell/code/repositories/relativisticpy/examples/alice.txt'
metadata_file_path = '/Users/ashleycottrell/code/repositories/relativisticpy/examples/compressed_alice.txt'
comp_data_file_path = '/Users/ashleycottrell/code/repositories/relativisticpy/examples/comp_alice_bytes.huff'
decoded_output_path = '/Users/ashleycottrell/code/repositories/relativisticpy/examples/decoded.txt'

huffman_tree = HuffmanTree.from_file(data_file_path)
huffman_tree.save_to_file(comp_data_file_path, metadata_file_path)

import os

os.path.getsize(data_file_path) - os.path.getsize(comp_data_file_path)