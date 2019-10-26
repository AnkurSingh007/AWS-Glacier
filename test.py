import unittest
import archive as target


class test(unittest.TestCase):
    def test_incorrect_filenames_are_filtered(self):
        filename_list = ['wrong_file_name.txt']
        filtered_list = target.filter_archive_candidate_list(filename_list)
        self.assertListEqual(filtered_list, [])

    def test_correct_filenames_are_not_filtered(self):
        filename_list = ['test-resources']
        filtered_list = target.filter_archive_candidate_list(filename_list)
        self.assertListEqual(filtered_list, ['test-resources'])
        

if __name__ == '__main__':
    unittest.main()
