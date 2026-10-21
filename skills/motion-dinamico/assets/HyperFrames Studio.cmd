@echo off
title HyperFrames Studio
rem Abre a tela de edicao do HyperFrames (Studio) no navegador.
rem Sem nada: abre o projeto do video do cerebro. Para abrir outro projeto, arraste a pasta dele em cima deste atalho.
rem Deixe esta janela preta aberta enquanto edita; fechar a janela fecha o Studio.
set "PROJ=%~1"
if not "%PROJ%"=="" goto abrir
for /d %%D in ("%USERPROFILE%\Desktop\Projetos Edi*") do set "PROJ=%%D\Motion Designer\videos\cerebro-dinamico"
:abrir
if not exist "%PROJ%\index.html" (
  echo Nao achei um projeto do HyperFrames em:
  echo %PROJ%
  pause
  exit /b 1
)
cd /d "%PROJ%"
echo Abrindo o HyperFrames Studio... (deixe esta janela aberta enquanto edita)
call npx hyperframes preview . --port 3002
pause
