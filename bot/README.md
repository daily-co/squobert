# Squobert's Botfile

This is a pretty standard Pipecat botfile. You can run it with `python bot.py -t daily` to use the DailyTransport, and follow the general instructions to deploy it to Pipecat Cloud.

## Sending facial expressions

Squobert's face is animated by sending `RTVIServerMessageFrames` to the client. Several existing frame types are handled in the `BotFaceProcessor` class. That's the easiest place to add more facial expression control.

## Displaying thought bubble text

If you push an `RTVIServerMessageFrame` with an `event` type of `show_text`, The client will display that text as a thought bubble. See the `LLMSearchResponseFrame` handler for an example.

## Scripting responses

I use a `ScriptProcessor` to pre-script responses when I make videos. (LLMs are clever, but not quite that clever yet.) You can see an example `script` object at the top of the botfile. If you don't provide a script to the processor, the LLM will just operate normally.
