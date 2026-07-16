import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ARTIST = "artist"
    PRODUCER = "producer"
    GUEST = "guest"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, enum.Enum):
    STEM_SEPARATION = "stem_separation"
    VOICE_TRAINING = "voice_training"
    VOICE_CONVERSION = "voice_conversion"
    MASTERING = "mastering"
