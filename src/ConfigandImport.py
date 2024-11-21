from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd

# Initialize base class for SQLAlchemy models
Base = declarative_base()  # Base class for all models
engine = create_engine("sqlite:///DataDB_new.db")  # Create the SQLite database
Session = sessionmaker(bind=engine)  # Session factory bound to the engine
session = Session()  # Create a new session


class Parent(Base):
    """
    A parent class for handling common functionalities such as importing CSV data and setting up the database.

    Attributes:
        __abstract__ (bool): Indicates that this class is abstract and not intended for table creation.
    """
    __abstract__ = True  # Indicates this is an abstract class, not for table creation.

    @classmethod
    def importcsv(cls, file, session):
        """
        Imports data from a CSV file and inserts it into the database table represented by the calling class.

        Args:
            file (str): Path to the CSV file to be imported.
            session (Session): SQLAlchemy session to be used for database operations.

        Raises:
            EmptyDataError: If the CSV file is empty.
            ParserError: If the CSV file cannot be parsed.
            KeyError: If an expected column is missing in the CSV file.
            Exception: For all other exceptions, the transaction is rolled back.
        """
        try:
            dataframe = pd.read_csv(file)
            for _, row in dataframe.iterrows():
                entry = cls(**row.to_dict())  # Convert each row into a dictionary and pass it to the class constructor
                session.add(entry)
            session.commit()  # Commit the session after adding all entries
            print(f"{file} successfully inserted into {cls.__tablename__}")
        except pd.errors.EmptyDataError:
            print(f"The file {file} is empty.")
        except pd.errors.ParserError:
            print(f"The file {file} could not be parsed.")
        except KeyError as ke:
            print(f"Expected column {ke} not found in {file}.")
        except Exception as e:
            session.rollback()  # Rollback the session in case of an error
            print(f"Error importing {file}: {str(e)}")

    @classmethod
    def setup_database(cls, db_path="sqlite:///DataDB_new.db"):
        """
        Sets up the database connection and returns the engine and session factory.

        Args:
            db_path (str): The database connection string (default is 'sqlite:///DataDB_new.db').

        Returns:
            tuple: A tuple containing the engine and session factory for the database.
        """
        print("Setting up database connection...")
        engine = create_engine(db_path)
        Session = sessionmaker(bind=engine)  # Create a new session factory bound to the engine
        print("Database connection established.")
        return engine, Session


# Define Trainingdata table
class Trainingdata(Parent):
    """
    Represents the 'trainingdata' table in the database.

    Attributes:
        x (float): Independent variable (primary key).
        y1 (float): Dependent variable 'y1 (training func)'.
        y2 (float): Dependent variable 'y2 (training func)'.
        y3 (float): Dependent variable 'y3 (training func)'.
        y4 (float): Dependent variable 'y4 (training func)'.
    """
    __tablename__ = "trainingdata"
    x = Column(Float, primary_key=True)
    y1 = Column(Float, name="y1 (training func)")
    y2 = Column(Float, name="y2 (training func)")
    y3 = Column(Float, name="y3 (training func)")
    y4 = Column(Float, name="y4 (training func)")


# Define Idealfunctions table
class Idealfunctions(Parent):
    """
    Represents the 'idealfunctions' table in the database.

    Attributes:
        x (float): Independent variable (primary key).
        y1 to y50 (float): Dependent variables 'y1 (ideal func)' to 'y50 (ideal func)'.
    """
    __tablename__ = "idealfunctions"
    x = Column(Float, primary_key=True)

# Add columns for y1 to y50 dynamically
for i in range(1, 51):
    setattr(Idealfunctions, f"y{i}", Column(Float, name=f"y{i} (ideal func)"))


# Define Testdata table
class Testdata(Parent):
    """
    Represents the 'testdata' table in the database.

    Attributes:
        id (int): Auto-incremented primary key.
        x (float): Independent variable.
        y (float): Dependent variable.
    """
    __tablename__ = "testdata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Float)
    y = Column(Float)


# Only run this part when the script is executed directly
if __name__ == "__main__":
    # Drop existing tables and create new ones
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Import CSV data into the database
    Trainingdata.importcsv("train.csv", session)
    Idealfunctions.importcsv("ideal.csv", session)
    Testdata.importcsv("test.csv", session)

    # Close the session after importing
    session.close()
