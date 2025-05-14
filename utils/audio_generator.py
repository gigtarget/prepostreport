import os
import boto3

def generate_audio_with_polly(script_text, voice_id="Kajal", output_path="./output/output_polly.mp3"):
    neural_supported = ["Raveena", "Kajal", "Karan", "Neerja"]
    engine_type = "neural" if voice_id in neural_supported else "standard"

    polly = boto3.client("polly", region_name="ap-south-1")  # Mumbai region for Indian voices

    try:
        response = polly.synthesize_speech(
            Text=script_text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine_type
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response["AudioStream"].read())

        print(f"✅ Polly audio saved to: {output_path} using {voice_id} ({engine_type})")
        return output_path

    except Exception as e:
        print(f"❌ Error generating Polly audio: {e}")
        return None
