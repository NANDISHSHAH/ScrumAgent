#!/bin/bash
model_name="llama3.1"
custom_model_name="llama_scrum"
ollama pull $model_name
ollama create $custom_model_name -f ./LLama3model