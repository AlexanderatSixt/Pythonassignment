import sys
import os
import unittest

# Add the 'src' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Now import your module
from ConfigandImport import Parent
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

class TestConfigAndImport(unittest.TestCase):

    def test_setup_database(self):
        """Test that setup_database creates an engine and a sessionmaker."""
        # Call the setup_database method
        engine, Session = Parent.setup_database("sqlite:///:memory:")  # Use an in-memory database for testing

        # Check that engine is an instance of the correct SQLAlchemy class
        self.assertIsInstance(engine, Engine)

        # Check that Session is a sessionmaker instance
        self.assertIsInstance(Session, sessionmaker)

if __name__ == '__main__':
    unittest.main()