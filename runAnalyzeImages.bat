:: runScoreTool.bat
:: tcornish 3/27/2014

:: launches an imagej-based algorithm written in jython

:: most of this is just to find JAVA_HOME, that code is
:: originally from http://www.rgagnon.com/javadetails/java-0642.html
:: see the version in the comments, not the original post

@echo off
cls
setlocal ENABLEEXTENSIONS
set KEY_NAME="HKLM\SOFTWARE\JavaSoft\Java Runtime Environment"
set WOW_KEY_NAME="HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\JavaSoft\Java Runtime Environment"
set VALUE_NAME=CurrentVersion
::
:: get the current version
::
:: check for the version that is native to 32 bit or 64 bit Windows
FOR /F "usebackq skip=2 tokens=3" %%A IN (`REG QUERY %KEY_NAME% /v %VALUE_NAME% 2^>nul`) DO (
    set ValueValue=%%A
)

if defined ValueValue (
    :: we found the native
    echo %KEY_NAME%\%VALUE_NAME% found.
    echo the current Java runtime is  %ValueValue%
    set JAVA_CURRENT="HKLM\SOFTWARE\JavaSoft\Java Runtime Environment\%ValueValue%"
) else (
    echo %KEY_NAME%\%VALUE_NAME% not found.
    :: check for a 32 bit Java on a 64 bit Windows (WOW)
    FOR /F "usebackq skip=2 tokens=3" %%A IN (`REG QUERY %WOW_KEY_NAME% /v %VALUE_NAME% 2^>nul`) DO (
        set ValueValue=%%A
    )
    if defined ValueValue (
        :: we found the 32 bit version in WOW
        echo %WOW_KEY_NAME%\%VALUE_NAME% found.
        echo the current Java runtime is  %ValueValue%
        set JAVA_CURRENT="HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\JavaSoft\Java Runtime Environment\%ValueValue%"
    ) else (
        echo %WOW_KEY_NAME%\%VALUE_NAME% not found.
        goto end
    )
)

set JAVA_HOME=JavaHome
::
:: get the javahome
::
FOR /F "usebackq skip=2 tokens=3*" %%A IN (`REG QUERY %JAVA_CURRENT% /v %JAVA_HOME% 2^>nul`) DO (
    set JAVA_PATH=%%A %%B
)


:: presumably we have found the path in the registry or quit
echo the path of the current Java JVM according to the registry is
echo %JAVA_PATH%
echo.
echo now if we try it :
"%JAVA_PATH%\bin\java.exe" -version
:end

:: Now actually start up jython via java
"%JAVA_PATH%\bin\java.exe" "-Dpython.home=." -classpath ".\lib\jython.jar;%CLASSPATH%" org.python.util.jython -Dpython.path=".\lib\ij.jar;." .\lib\analyze_images.py %*

:: wait for a keypress then exit
pause
