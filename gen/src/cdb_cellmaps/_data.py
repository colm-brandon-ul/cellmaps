from abc import ABC
from io import BytesIO
import sys
from urllib.parse import urlparse
import requests
from typing import Dict, Iterable, Iterator, List, Tuple, TypeVar, Set, Generic
from ._deps import HasDependencies
from pathlib import Path
import os
from ._config import Config
from ._utils import get_minio_client
from .data_utils import Prefix

if sys.version_info >= (3, 8):
    from typing import Protocol as Protocol
else:
    from typing_extensions import Protocol


K = TypeVar('K')
V = TypeVar('V')
Type = TypeVar('Type')
T = TypeVar('T')

class SyntacticData(ABC):
    def __init__(self) -> None:
        super().__init__()

# Semantic Data Types

class SemanticData(ABC):
    def __init__(self) -> None:
        super().__init__()
        
        # overridden methods for displaying the objects variables as strings
    def __str__(self) -> str:
        return str({name: value for name,value in self.__dict__.items() if not callable(value) and not name.startswith("__")})
    
    def __repr__(self) -> str:
        return repr({name: value for name,value in self.__dict__.items() if not callable(value) and not name.startswith("__")})


# Returns a collection (i.e. an iterable) 
class NonAtomic(SemanticData):
    def __init__(self) -> None:
        super().__init__()

class Atomic(SemanticData):
    def __init__(self) -> None:
        super().__init__()


class DataStructure(SyntacticData):
    ...

# Data Structures
class HashMapMixin(Generic[K,V], DataStructure):
    data: Dict[K,V]
    
    def __getitem__(self,key: K) -> V:
        return self.data[key]
    
    def __setitem__(self, key: K, value: V) -> None:
        self.data[key] = value
        
    def __delitem__(self, key: K) -> None:
        del self.data[key]
        
    def __contains__(self,key: K) -> bool:
        return key in self.data
    
    def __len__(self) -> int:
        return len(self.data)
    
    def keys(self) -> List[K]:
        return list(self.data.keys())
    
    def values(self) -> List[V]:
        return list(self.data.values())
    
    def items(self) -> List[Tuple[K,V]]:
        return list(self.data.items())
    
    def clear(self) -> None:
        self.data.clear()
        
    def copy(self) -> "HashMapMixin[K,V]":
        new_dict = self.__class__()
        new_dict.data = self.data.copy()
        return new_dict
    
    def update(self, other_dict: "HashMapMixin[K,V]") -> None:
        self.data.update(other_dict.data)
        
    def __str__(self) -> str:
        return str(self.data)
    
    def __repr__(self) -> str:
        return repr(self.data)
    
class ListMixin(Iterable,Generic[V],DataStructure):
    data: List[V]
    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index) -> V:
        return self.data[index]

    def __setitem__(self, index, value: V):
        self.data[index] = value

    def __delitem__(self, index):
        del self.data[index]

    def append(self, value: V):
        self.data.append(value)

    def extend(self, iterable: Iterable[V]):
        self.data.extend(iterable)

    def insert(self, index, value: V):
        self.data.insert(index, value)

    def remove(self, value: V):
        self.data.remove(value)

    def pop(self, index=-1) -> V:
        return self.data.pop(index)

    def index(self, value: V) -> int:
        return self.data.index(value)

    def count(self, value: V) -> int:
        return self.data.count(value)

    def sort(self):
        self.data.sort()

    def reverse(self):
        self.data.reverse()

    def __iter__(self) -> Iterator[V]:
        return iter(self.data)
    
class SetMixin(Iterable, Generic[V], DataStructure):
    data: Set[V]
    
    def __len__(self) -> int:
        return len(self.data)
    
    def add(self, value: V):
        self.data.add(value)
    
    def remove(self, value: V):
        self.data.remove(value)
    
    def discard(self, value: V):
        self.data.discard(value)
    
    def pop(self) -> V:
        return self.data.pop()
    
    def clear(self):
        self.data.clear()
    
    def update(self, iterable: Iterable[V]):
        self.data.update(iterable)
    
    def difference_update(self, iterable: Iterable[V]):
        self.data.difference_update(iterable)
    
    def intersection_update(self, iterable: Iterable[V]):
        self.data.intersection_update(iterable)
    
    def symmetric_difference_update(self, iterable: Iterable[V]):
        self.data.symmetric_difference_update(iterable)
    
    def __contains__(self, value: V) -> bool:
        return value in self.data
    
    def __iter__(self) -> Iterator[V]:
        return iter(self.data)

# Primitive s
class StringMixin:
    def append(self, text):
        # Custom method to append text to the string
        return self.__class__(self + text)

    def reverse(self):
        # Custom method to reverse the string
        return self.__class__(self[::-1])
    


 
class File(HasDependencies,SyntacticData):
    """
    Base mixin class for handling various file types across local and object storage
    """
    FILE_EXTENSION: str = ''
    
    def __init__(self, url: str) -> None:
        """
        Initialize the file handler with a URL
        
        :param url: Path or URL to the file
        """
        self.url: str = url
    
    def get_external_url(self) -> str:
        """
        Get the external URL of the file
        
        :return: External URL
        """

        parser_external_url = urlparse(os.environ.get('CINCODEBIO_BASE_URL'))
        parsed_url = urlparse(self.url)

        return parsed_url._replace(
            netloc=parser_external_url.netloc,
            path=str(Config._MINIO_PRESIGNED_INGRESS_PATH) + parsed_url.path # prepend the path with the minio presigned path
            ).geturl()
    
    @classmethod
    def write(cls, data, file_name: str, prefix: Prefix, rpy2: bool=False):
        """
        Write file to local or object storage based on configuration
        
        :param data: Data to be written
        :param file_name: Name of the file
        :param prefix: Path prefix for the file
        :param rpy2: Whether to use rpy2 for conversion (if applicable)

        :return: Any (see )
        """
        if Config.DEBUG:
            # Local file system writing
            base_path = Path("./")
            prefix_path = Path(prefix[1:]+file_name+cls.FILE_EXTENSION)
            import logging
            
            logging.warning(f"Writing to {base_path / prefix[1:]}")
            # Ensure directory exists
            os.makedirs(base_path / prefix[1:], exist_ok=True)
            
            # File type specific writing logic goes here
            cls._write_local(data, base_path / prefix_path, rpy2)
            
            url = str((base_path / prefix_path).absolute().as_posix())
        else:
            # Object storage writing
            url = cls._write_object_storage(data, file_name, prefix, rpy2)
        
        return cls(url=url)
    
    @classmethod
    def _write_local(cls, data, full_path,rpy2: bool):
        """
        Default local writing method to be overridden by specific file types
        """
        raise NotImplementedError("Subclass must implement abstract method")
    
    @classmethod
    def _write_object_storage(cls, data, file_name: str, prefix: str,rpy2: bool):
        """
        Write to object storage using Minio
        
        :param data: Data to be uploaded
        :param file_name: Name of the file
        :param prefix: Path prefix for the file
        :return: Presigned URL of the uploaded file
        """
        # Create buffer
        b_out = BytesIO()
        
        # Write data to buffer (to be implemented by specific file types)
        cls._buffer_write(data, b_out, rpy2)
        
        # Prepare upload
        bucket_name = Config.MINIO_WORKFLOW_BUCKET
        client = get_minio_client()
        full_object_name = f"{prefix}{file_name}{cls.FILE_EXTENSION}"
        
        # Upload to object storage
        client.put_object(
            bucket_name=bucket_name,
            object_name=full_object_name,
            data=b_out,
            num_parallel_uploads=Config._MINIO_NUM_PARALLEL_UPLOADS,
            length=b_out.getbuffer().nbytes
        )
        
        # Return presigned URL
        return client.get_presigned_url('GET', bucket_name, full_object_name)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        """
        Method to write specific file types to buffer
        """
        raise NotImplementedError("Subclass must implement abstract method")
    
    def read(self, rpy2: bool=False):
        """
        Read file from local or remote URL
        
        :return: File contents or object
        """
        if Config.DEBUG:
            return self._read_local(rpy2)
        else:
            return self._read_remote(rpy2)
    
    def _read_local(self, rpy2: bool=False):
        """
        Read from local file system
        """
        raise NotImplementedError("Subclass must implement abstract method")
    
    def _read_remote(self, rpy2: bool=False):
        """
        Read from remote URL
        """
        response = requests.get(self.url)
        return self._process_remote_content(response.content, rpy2)
    
    def _process_remote_content(self, content, rpy2: bool=False):
        """
        Process remote content for specific file types
        """
        raise NotImplementedError("Subclass must implement abstract method")


# Files
####### 3D MODELS #######
# FBX
class FBX(File):
    FILE_EXTENSION = '.fbx'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer)
    
    def _read_local(self, rpy2: bool):
        fbx = self.dep.require('fbx')
        return fbx.FBX(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        fbx = self.dep.require('fbx')
        return fbx.FBX(BytesIO(content))
    
# OBJ
class OBJ(File):
    FILE_EXTENSION = '.obj'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path)
        ...
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer)
        ...
    
    def _read_local(self, rpy2: bool):
        obj = self.dep.require('objloader')
        return obj.load(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        obj = self.dep.require('objloader')
        return obj.load(BytesIO(content))

# STL
class STL(File):
    FILE_EXTENSION = '.stl'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.export(full_path, format='stl') 
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.export(buffer, format='stl')
    
    def _read_local(self, rpy2: bool):
        mesh = self.dep.require('mesh')
        return mesh.Mesh.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        mesh = self.dep.require('mesh')
        return mesh.Mesh.from_file(BytesIO(content))

# AAC
class AAC(File):
    FILE_EXTENSION = '.aac'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.export(full_path, format='aac')
        ...
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.export(buffer, format='aac')
    
    def _read_local(self, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(BytesIO(content))

# FLAC
class FLAC(File):
    FILE_EXTENSION = '.flac'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.export(full_path, format='flac')

    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.export(buffer, format='flac')

    
    def _read_local(self, rpy2: bool):
        pydub = self.dep.require('pydub')
        return pydub.AudioSegment.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        pydub = self.dep.require('pydub')
        return pydub.AudioSegment.from_file(BytesIO(content))

# MP3
class MP3(File):
    FILE_EXTENSION = '.mp3'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.export(full_path, format='mp3')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.export(buffer, format='mp3')
    
    def _read_local(self, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(BytesIO(content))

# OGG
class OGG(File):
    FILE_EXTENSION = '.ogg'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.export(full_path, format='ogg')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.export(buffer, format='ogg')

    def _read_local(self, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(BytesIO(content))

# WAV
class WAV(File):
    FILE_EXTENSION = '.wav'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        audio = cls.deps().require('pydub')
        data.export(full_path, format='wav')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        audio = cls.deps().require('pydub')
        data.export(buffer, format='wav')
    
    def _read_local(self, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        audio = self.dep.require('pydub')
        return audio.AudioSegment.from_file(BytesIO(content))
      
####### Graph Data #######
# GML
class GML(File):
    FILE_EXTENSION = '.gml'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_gml(data, full_path)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_gml(data, buffer)

    
    def _read_local(self, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_gml(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_gml(BytesIO(content))
    
# GraphML
class GraphML(File):
    FILE_EXTENSION = '.graphml'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_graphml(data, full_path)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_graphml(data, buffer)
    
    def _read_local(self, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_graphml(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_graphml(BytesIO(content))
    
# PAJEKNET
class PajekNet(File):
    FILE_EXTENSION = '.pajek.net'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_pajek(data, full_path)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        nx = cls.deps().require('networkx')
        nx.write_pajek(data, buffer)
    
    def _read_local(self, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_pajek(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        nx = self.dep.require('networkx')
        return nx.read_pajek(BytesIO(content))
    
###### IMAGE #######
class OMETIFF(File):
    FILE_EXTENSION = '.ome.tiff'

    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        tifffile, np = cls.deps().require('tifffile', 'numpy')
        tifffile.imwrite(full_path, np.array(data),compression='zlib')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        tifffile, np = cls.deps().require('tifffile', 'numpy')
        tifffile.imwrite(buffer, np.array(data),compression='zlib')
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))

# Configuration and utility imports

# DICOM
class DICOM(File):
    FILE_EXTENSION = '.dcm'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        ...
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        ...
    
    def _read_local(self, rpy2: bool):
        pydicom = self.dep.require('pydicom')
        return pydicom.dcmread(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        pydicom = self.dep.require('pydicom')
        return pydicom.dcmread(BytesIO(content))
    
# BMP
class BMP(File):
    FILE_EXTENSION = '.bmp'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path, 'BMP')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer, 'BMP')
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))
    
# GIF
class GIF(File):
    FILE_EXTENSION = '.gif'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path, 'GIF')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer, 'GIF')
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))
    
# JPG
class JPG(File):
    FILE_EXTENSION = '.jpg'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path, 'JPEG')
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer, 'JPEG')
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))


# PNG
class PNG(File):
    FILE_EXTENSION = '.png'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.save(full_path, 'PNG')

    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.save(buffer, 'PNG')
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))


# SVG
class SVG(File):
    FILE_EXTENSION = '.svg'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        with open(full_path, 'w') as f:
            f.write(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        buffer.write(data)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            return f.read()
    
    def _process_remote_content(self, content, rpy2: bool):
        return content.decode('utf-8')
# TIFF
class TIFF(File):
    FILE_EXTENSION = '.tiff'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        tifffile = cls.deps().require('tifffile')
        with tifffile.TiffWriter(full_path) as tiff:
            tiff.save(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        tifffile = cls.deps().require('tifffile')
        with tifffile.TiffWriter(buffer) as tiff:
            tiff.save(data)
    
    def _read_local(self, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(self.url)
    
    def _process_remote_content(self, content, rpy2: bool):
        Image = self.dep.require(('PIL','Image'))
        return Image.open(BytesIO(content))


####### TABULAR DATA #######
# CSV
class CSV(File):
    FILE_EXTENSION = '.csv'

    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        pandas = cls.deps().require('pandas')
        if rpy2:
            ro = cls.deps().require('rpy2.robjects')
            with (ro.default_converter + ro.pandas2ri.converter).context():
                data = ro.conversion.rpy2py(data)
        data.to_csv(full_path, index=False)

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        pandas = cls.deps().require('pandas')
        if rpy2:
            ro = cls.deps().require('rpy2.robjects')
            with (ro.default_converter + ro.pandas2ri.converter).context():
                data = ro.conversion.rpy2py(data)
        data.to_csv(buffer, index=False)

    def _read_local(self, rpy2: bool):
        pandas = self.dep.require('pandas')
        if rpy2:
            ro = self.dep.require('rpy2.robjects')
            with (ro.default_converter + ro.pandas2ri.converter).context():
                return ro.conversion.py2rpy(pandas.read_csv(self.url))
        return pandas.read_csv(self.url)

    def _process_remote_content(self, content, rpy2: bool):
        pandas = self.dep.require('pandas')
        if rpy2:
            ro = self.dep.require('rpy2.robjects')
            with (ro.default_converter + ro.pandas2ri.converter).context():
                return ro.conversion.py2rpy(pandas.read_csv(BytesIO(content)))
        return pandas.read_csv(BytesIO(content))


# TSV
class TSV(File):
    FILE_EXTENSION = '.tsv'

    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        pandas = cls.deps().require('pandas')
        data.to_csv(full_path, sep='\t', index=False)

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        pandas = cls.deps().require('pandas')
        data.to_csv(buffer, sep='\t', index=False)

    def _read_local(self, rpy2: bool):
        pandas = self.dep.require('pandas')
        return pandas.read_csv(self.url, sep='\t')

    def _process_remote_content(self, content, rpy2: bool):
        pandas = self.dep.require('pandas')
        return pandas.read_csv(BytesIO(content), sep='\t')

    
####### VIDEO #######

# AVI
class AVI(File):
    FILE_EXTENSION = '.avi'

    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        
        data.write_videofile(full_path)
        ...

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        
        data.write_videofile(buffer)

    def _read_local(self, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(self.url)

    def _process_remote_content(self, content, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(BytesIO(content))

    
# MOV
class MOV(File):
    FILE_EXTENSION = '.mov'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        data.write_videofile(full_path )

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        data.write_videofile(buffer)

    def _read_local(self, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(self.url)

    def _process_remote_content(self, content, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(BytesIO(content))

# MP4
class MP4(File):
    FILE_EXTENSION = '.mp4'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        
        data.write_videofile(full_path)

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        
        data.write_videofile(buffer)
        ...

    def _read_local(self, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(self.url)

    def _process_remote_content(self, content, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(BytesIO(content))
# MPEG
class MPEG(File):
    FILE_EXTENSION = '.mpeg'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        
        data.write_videofile(full_path)
        ...

    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        
        data.write_videofile(buffer)
        ...

    def _read_local(self, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(self.url)

    def _process_remote_content(self, content, rpy2: bool):
        moviepy = self.dep.require('moviepy.editor')
        return moviepy.VideoFileClip(BytesIO(content))

####### TEXT #######
# HTML
class HTML(File):
    FILE_EXTENSION = '.html'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        with open(full_path, 'w') as f:
            f.write(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        buffer.write(data)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            return f.read()
    
    def _process_remote_content(self, content, rpy2: bool):
        return content.decode('utf-8')

# JSON
class JSON(File):
    FILE_EXTENSION = '.json'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        json = cls.deps().require('json')
        with open(full_path, 'w') as f:
            json.dump(data, f)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        json = cls.deps().require('json')
        json.dump(data, buffer)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            json = self.dep.require('json')
            return json.load(f)
    
    def _process_remote_content(self, content, rpy2: bool):
        json = self.dep.require('json')
        return json.loads(content)
    
# MD
class MD(File):
    FILE_EXTENSION = '.md'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        with open(full_path, 'w') as f:
            f.write(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        buffer.write(data)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            return f.read()
    
    def _process_remote_content(self, content, rpy2: bool):
        return content.decode('utf-8')

# TXT
class TXT(File):
    FILE_EXTENSION = '.txt'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        with open(full_path, 'w') as f:
            f.write(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        buffer.write(data)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            return f.read()
    
    def _process_remote_content(self, content, rpy2: bool):
        return content.decode('utf-8')

# XML
class XML(File):
    FILE_EXTENSION = '.xml'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        with open(full_path, 'w') as f:
            f.write(data)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        buffer.write(data)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            return f.read()
    
    def _process_remote_content(self, content, rpy2: bool):
        return content.decode('utf-8')
# YAML
class YAML(File):
    FILE_EXTENSION = '.yaml'
    @classmethod
    def _write_local(cls, data, full_path, rpy2: bool):
        yaml = cls.deps().require('pyyaml')
        with open(full_path, 'w') as f:
            yaml.dump(data, f)
    
    @classmethod
    def _buffer_write(cls, data, buffer, rpy2: bool):
        yaml = cls.deps().require('pyyaml')
        yaml.dump(data, buffer)
    
    def _read_local(self, rpy2: bool):
        with open(self.url, 'r') as f:
            yaml = self.dep.require('pyyaml')
            return yaml.load(f, Loader=yaml.FullLoader)
    
    def _process_remote_content(self, content, rpy2: bool):
        yaml = self.dep.require('pyyaml')
        return yaml.load(content, Loader=yaml.FullLoader)