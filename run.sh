W=4
H=4
D=2
R=3
N=2

BRL=001021

python -u search.py --arch='mesh' --w=${W} --h=${H} --d=${D} --r=${R} --n=${N} --brl=${BRL} --bab --opt
# python -u search.py --arch='cube' --w=${W} --h=${H} --d=${D} --r=${R} --n=${N} --brl=${BRL} --mp --pn=10
# python -u search.py --arch='mesh' --w=${W} --h=${H} --r=${R} --n=${N} --brl=${BRL} --mp --pn=10 --bab
# python -u search.py --arch='mesh' --w=${W} --h=${H} --r=${R} --n=${N} --brl=${BRL} --mp --pn=10
# python -u search.py --arch='mesh' --w=${W} --h=${H} --r=${R} --n=${N} --brl=${BRL} --opt --popt --bab