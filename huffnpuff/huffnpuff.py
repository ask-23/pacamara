# Huffman encoder / Korzybski tool


import unittest
import os
import heapq
from typing import Dict, List, Optional, Tuple


class Node:
    """
    This class defines the parts used to build a Huffman tree

    Comprises:
        char: Character stored in the node
        freq: Frequency of the character
        left: Left child node
        right: Right child node
    """

    def __init__(self, char: str, freq: int) -> None:
        self.char = char
        self.freq = freq
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __lt__(self, other: 'Node') -> bool:
        return self.freq < other.freq


class HuffmanEncoder:
    """
    The class implements Huffman encoding with the following Methods:

        compress: Main method to compress input file
        make_frequency_dict: Creates frequency dictionary from input text
        make_heap: Creates min heap from frequency dictionary
        merge_nodes: Merges nodes to create Huffman tree
        make_codes: Generates Huffman codes for each character
        get_encoded_text: Converts input text to encoded binary string
        pad_encoded_text: Adds padding to make byte-aligned binary string
    """

    def __init__(self):
        self.heap: List[Node] = []
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
        self.padding: int = 0

    def make_frequency_dict(self, text: str) -> Dict[str, int]:
        """Creates frequency dictionary from input text"""
        freq_dict = {}
        for char in text:
            freq_dict[char] = freq_dict.get(char, 0) + 1
        return freq_dict

    def make_heap(self, freq_dict: Dict[str, int]) -> None:
        """Creates min heap from frequency dictionary"""
        for char, freq in freq_dict.items():
            node = Node(char, freq)
            heapq.heappush(self.heap, node)

    def merge_nodes(self) -> None:
        """Merges nodes to create Huffman tree"""
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, node: Optional[Node], current_code: str) -> None:
        """Recursive helper function for make_codes"""
        if node is None:
            return

        if node.char is not None:
            self.codes[node.char] = current_code
            self.reverse_codes[current_code] = node.char
            return

        self.make_codes_helper(node.left, current_code + "0")
        self.make_codes_helper(node.right, current_code + "1")

    def make_codes(self) -> None:
        """Generates Huffman codes for each character"""
        root = heapq.heappop(self.heap)
        self.make_codes_helper(root, "")

    def get_encoded_text(self, text: str) -> str:
        """Converts input text to encoded binary string"""
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text: str) -> Tuple[str, int]:
        """Adds padding to make byte-aligned binary string"""
        padding = 8 - (len(encoded_text) % 8)
        encoded_text += "0" * padding
        self.padding = padding
        return encoded_text, padding

    def compress(self, input_file: str) -> str:
        """Main method to compress input file"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found")

        with open(input_file, 'r') as file:
            text = file.read()

        freq_dict = self.make_frequency_dict(text)
        self.make_heap(freq_dict)
        self.merge_nodes()
        self.make_codes()
        encoded_text = self.get_encoded_text(text)
        padded_text, padding = self.pad_encoded_text(encoded_text)

        # Convert binary string to bytes
        final_bytes = bytearray()
        for i in range(0, len(padded_text), 8):
            byte = padded_text[i:i + 8]
            final_bytes.append(int(byte, 2))

        output_file = input_file + ".bin"
        with open(output_file, 'wb') as file:
            file.write(bytes([padding]))  # Store padding information
            file.write(bytes(final_bytes))

        return output_file


class TestHuffmanEncoder(unittest.TestCase):
    """Test cases for the HuffmanEncoder class"""

    def setUp(self):
        self.encoder = HuffmanEncoder()
        self.test_text = "AABBBCCCC"
        self.empty_text = ""

    def test_frequency_dict(self):
        freq = self.encoder.make_frequency_dict(self.test_text)
        self.assertEqual(freq['A'], 2)
        self.assertEqual(freq['B'], 3)
        self.assertEqual(freq['C'], 4)

    def test_empty_input(self):
        freq = self.encoder.make_frequency_dict(self.empty_text)
        self.assertEqual(len(freq), 0)

    def test_heap_creation(self):
        freq = self.encoder.make_frequency_dict(self.test_text)
        self.encoder.make_heap(freq)
        self.assertEqual(len(self.encoder.heap), 3)

    def test_encoding_process(self):
        freq = self.encoder.make_frequency_dict(self.test_text)
        self.encoder.make_heap(freq)
        self.encoder.merge_nodes()
        self.encoder.make_codes()
        encoded = self.encoder.get_encoded_text(self.test_text)
        self.assertTrue(all(c in '01' for c in encoded))

    def test_padding(self):
        encoded_text = "1010101"
        padded_text, padding = self.encoder.pad_encoded_text(encoded_text)
        self.assertEqual(len(padded_text) % 8, 0)
        self.assertEqual(padding, 1)


def main():
    """
    Main function to run the compression tool
    Usage: python3 huffnpuff.py
    """
    # Run tests first
    unittest.main(argv=[''], exit=False)

    print("\n=== Huffman Compression Tool ===")
    print("You give it a file and it will be compressed - a bit) \n")

    huffman = HuffmanEncoder()
    try:
        input_file = input("Type your filename here (textfiles only):")
        compressed_file = huffman.compress(input_file)
        print(f"\nCompressed file created: {compressed_file}")

        # Calculate and display compression statistics
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(compressed_file)
        compression_ratio = (1 - compressed_size / original_size) * 100

        print("\nCompression Results:")
        print(f"Original file size: {original_size} bytes")
        print(f"Compressed file size: {compressed_size} bytes")
        print(f"Compression ratio: {compression_ratio:.2f}%")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please make sure the file exists and you have proper permissions.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()