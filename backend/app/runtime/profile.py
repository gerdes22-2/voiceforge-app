from pydantic import BaseModel, Field

class ResourceProfile(BaseModel):
    """
    Declares the resource requirements and capabilities of an AI Provider.
    """
    gpu_required: bool = Field(default=False, description="Does this provider require a GPU?")
    min_vram_mb: int = Field(default=0, description="Minimum VRAM required in MB")
    min_ram_mb: int = Field(default=1024, description="Minimum System RAM required in MB")
    expected_runtime_sec: int = Field(default=300, description="Expected time to complete standard task")
    
    # Capabilities
    supports_cache: bool = Field(default=True, description="Can the output of this provider be cached?")
    supports_resume: bool = Field(default=False, description="Can this provider resume from partial state?")
    supports_cancellation: bool = Field(default=True, description="Can this provider be gracefully cancelled?")
