### Short description
An attemption of using the compiled *C* library, which is controling the work
of _Avantes_ spectometers, for controling the work of the spectometer in *Python*

(based on __libavs.so.0.2.0__ which should be placed in that folder)

#### Avantes library _libavs.so.0.2.0_ specified file
* `avantes_func.py` - library limited functions declaration in Python
* `structures.py` - structures declaration (also functions for those structures)
* `error_codes.py` - possible error codes from the library

#### Communication example
* `mqueues.py` - a base which provides a basic communication
by sending or receiving a data (which is moslty a dictionary,
packed with a `pickle` module) 

* `receiver_parser.py` - receiver cli arguments parser
* `receiver.py` - reading queue might be specified,
but it's better to set a queue same as *ID* of spectometer
* `sender_parser.py` - sender cli arguments parser
* `sender.py` - for processing passed arguments and sending an appropriate message

#### Device specified functions
* `device.py` - place for specifing the workflow of the device

#### For the testing purpose only
* `data.py` - saving the obtained data to a csv (data.csv is used in `flask` app)

#### Additional files
* `debug.py` - logger configuration and debug decorator
* `initialize.py` - might be used as a startup script, 
when the device connected via *USB*
* `avantes.rules` - *USB* rules specified for avantes spectometers 
(place where startup script should be added)
* `avantes_log.conf` - logger configuration
* `ava_default.json` - *IMPORTANT* avantes basic configuration file.
All changes better to do in _user defined file_ (ava_user.json) and pass it
as a parameter for startup config or change it at runtime with appropriate
message/function call
* `ava_user.json` - _user defined_ avantes configuration file
