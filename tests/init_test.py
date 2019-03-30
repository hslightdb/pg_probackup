import os
import unittest
from .helpers.ptrack_helpers import dir_files, ProbackupTest, ProbackupException


module_name = 'init'


class InitTest(ProbackupTest, unittest.TestCase):

    # @unittest.skip("skip")
    # @unittest.expectedFailure
    def test_success(self):
        """Success normal init"""
        fname = self.id().split(".")[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(base_dir=os.path.join(module_name, fname, 'node'))
        self.init_pb(backup_dir)
        self.assertEqual(
            dir_files(backup_dir),
            ['backups', 'wal']
        )
        self.add_instance(backup_dir, 'node', node)
        self.assertEqual("INFO: Instance 'node' successfully deleted\n", self.del_instance(backup_dir, 'node'),
            '\n Unexpected Error Message: {0}\n CMD: {1}'.format(repr(self.output), self.cmd))

        # Show non-existing instance
        try:
            self.show_pb(backup_dir, 'node')
            self.assertEqual(1, 0, 'Expecting Error due to show of non-existing instance. Output: {0} \n CMD: {1}'.format(
                repr(self.output), self.cmd))
        except ProbackupException as e:
            self.assertEqual(e.message,
                "ERROR: Instance 'node' does not exist in this backup catalog\n",
                '\n Unexpected Error Message: {0}\n CMD: {1}'.format(e.message, self.cmd))

        # Delete non-existing instance
        try:
            self.del_instance(backup_dir, 'node1')
            self.assertEqual(1, 0, 'Expecting Error due to delete of non-existing instance. Output: {0} \n CMD: {1}'.format(
                repr(self.output), self.cmd))
        except ProbackupException as e:
            self.assertEqual(e.message,
                "ERROR: Instance 'node1' does not exist in this backup catalog\n",
                '\n Unexpected Error Message: {0}\n CMD: {1}'.format(e.message, self.cmd))

        # Add instance without pgdata
        try:
            self.run_pb([
                "add-instance",
                "--instance=node1",
                "-B", backup_dir
            ])
            self.assertEqual(1, 0, 'Expecting Error due to adding instance without pgdata. Output: {0} \n CMD: {1}'.format(
                repr(self.output), self.cmd))
        except ProbackupException as e:
            self.assertEqual(e.message,
                "ERROR: Required parameter not specified: PGDATA (-D, --pgdata)\n",
                '\n Unexpected Error Message: {0}\n CMD: {1}'.format(e.message, self.cmd))

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_already_exist(self):
        """Failure with backup catalog already existed"""
        fname = self.id().split(".")[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(base_dir=os.path.join(module_name, fname, 'node'))
        self.init_pb(backup_dir)
        try:
            self.show_pb(backup_dir, 'node')
            self.assertEqual(1, 0, 'Expecting Error due to initialization in non-empty directory. Output: {0} \n CMD: {1}'.format(
                repr(self.output), self.cmd))
        except ProbackupException as e:
            self.assertEqual(e.message,
                "ERROR: Instance 'node' does not exist in this backup catalog\n",
                '\n Unexpected Error Message: {0}\n CMD: {1}'.format(repr(e.message), self.cmd))

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_abs_path(self):
        """failure with backup catalog should be given as absolute path"""
        fname = self.id().split(".")[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(base_dir=os.path.join(module_name, fname, 'node'))
        try:
            self.run_pb(["init", "-B", os.path.relpath("%s/backup" % node.base_dir, self.dir_path)])
            self.assertEqual(1, 0, 'Expecting Error due to initialization with non-absolute path in --backup-path. Output: {0} \n CMD: {1}'.format(
                repr(self.output), self.cmd))
        except ProbackupException as e:
            self.assertEqual(e.message,
                "ERROR: -B, --backup-path must be an absolute path\n",
                '\n Unexpected Error Message: {0}\n CMD: {1}'.format(repr(e.message), self.cmd))

        # Clean after yourself
        self.del_test_dir(module_name, fname)
