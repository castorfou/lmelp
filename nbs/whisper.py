# AUTOGENERATED! DO NOT EDIT! File to edit: 09 whisper mp3.ipynb.

# %% auto 0
__all__ = ["AUDIO_PATH", "list_mp3_files", "extract_whisper", "store_whisper_in_db"]

# %% 09 whisper mp3.ipynb 2
AUDIO_PATH = "audios"

# %% 09 whisper mp3.ipynb 4
from download import get_audio_path
import os, glob


def list_mp3_files(audio_path=AUDIO_PATH):
    fullpath = get_audio_path(audio_path)

    return glob.glob(os.path.join(fullpath, "*.mp3"))


# %% 09 whisper mp3.ipynb 7
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


def extract_whisper(mp3_filename):

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )

    dataset = load_dataset(
        "distil-whisper/librispeech_long", "clean", split="validation"
    )
    sample = dataset[0]["audio"]

    result = pipe(
        mp3_filename,
        return_timestamps=True,
    )

    return result["text"]


# %% 09 whisper mp3.ipynb 10
from bson import ObjectId


def store_whisper_in_db(whisper, collection, oid, force=False, verbose=False):
    """
    whisper: str, la transcription du fichier audio
    collection: pymongo collection
    oid: str, l'identifiant de l episode
    force: bool, si True, on ecrase le whisper existant

    return True si le whisper a ete stocke, False sinon
    """

    # Récupération du document
    document_entry = collection.find_one({"_id": ObjectId(oid)})

    if document_entry is None:
        if verbose:
            print(f"Document avec l'oid {oid} non trouvé")
        return False

    if "whisper" in document_entry and not force:
        if verbose:
            print(
                f"Whisper déjà stocké pour l'oid {oid}m et on ne force pas le stockage"
            )
        return False
    else:
        document_entry["whisper"] = whisper
        collection.update_one({"_id": ObjectId(oid)}, {"$set": document_entry})
        if verbose:
            print(f"Whisper stocké pour l'oid {oid}")
        return True
