# Rodada matinal automática da Prospecção SDR (chamada pelo Agendador de Tarefas).
# Gera um Excel datado em .\saidas e registra o log do dia. Por segurança, NÃO
# empurra pro Agendor por padrão (evita duplicar organizações a cada manhã).
# Para também subir os quentes ao CRM, acrescente na linha do python:
#     --enviar-agendor --temperatura quente

$ErrorActionPreference = "Continue"
$proj = "C:\Users\pedro.porpino\prospeccao-sdr"
$py   = "C:\Program Files\Python314\python.exe"
Set-Location $proj
$env:PYTHONIOENCODING = "utf-8"

New-Item -ItemType Directory -Force -Path "$proj\saidas" | Out-Null
$data = Get-Date -Format "yyyy-MM-dd"
$saida = "$proj\saidas\leads_$data.xlsx"
$log   = "$proj\saidas\log_$data.txt"

& $py "$proj\cli.py" --fontes pncp sigmine --uf AM PA RO RR AC AP TO --limite 40 --saida $saida *>> $log
