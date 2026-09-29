from dataclasses import dataclass


@dataclass
class Source:
    source_id: str
    source_name: str
    audio_path: str
    source_type: str