#!/usr/bin/python3

import sys,csv,re
import unicodedata as ud
import locale
locale.setlocale(locale.LC_NUMERIC, "nb_NO.UTF-8")
locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

expr=re.compile('(.): (\d+) \((\d+\.\d+)%\)')

def readCustom(src):
  data=dict()
  with open(src, 'r') as srcfile:
    while True:
      l = srcfile.readline()
      if not l:
        break
      m=expr.match(l)
      c=m.group(1)
      count=int(m.group(2))
      p=float(m.group(3))
      data[c]={'count': count, 'ratio': p}
  return data

def writeCsv(dest, data, fieldnames=None):
    if not fieldnames:
      fieldnames=set()
      for row in data:
        fieldnames|=row.keys()

    with open(dest, 'w', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      for row in data:
        d=dict()
        d['char']=row
        d={**d, **data[row]}
        writer.writerow(d)

def sum(a,b):
  retval=dict()
  for key in (a.keys() | b.keys()):
    val = None
    if key in a:
      val=a[key]
      if key in b:
        val=val+b[key]
    else:
      val=b[key]

    retval[key]=val

  return retval

  raise 'Not finished'

def lower(data):
    res=dict()
    for ch in data:
      nch = ch.lower()
      if not nch in res:
        res[nch]=data[ch]
      else:
        res[nch]=sum(res[nch],data[ch])
    return res

def unsuper(data):
    res=dict()
    for ch in data:
      desc = ud.name(ch)
      desc=desc.replace('SUPERSCRIPT ', '')
      try:
        print('%s: %s' % (ch,desc))
        nch = ud.lookup(desc)
      except KeyError:
        raise ('Invalid character %s' % (desc) )
      if not nch in res:
        res[nch]=data[ch]
      else:
        res[nch]=sum(res[nch],data[ch])
    return res

def normalizeAlphabet(data, alphabet):
    res=dict()
    for ch in data:
      desc = ud.name(ch)
      nch = ud.normalize('NFC', ch)
      if nch not in alphabet:
        desc = ud.name(ch)
        cutoff = desc.find(' WITH ')
        if cutoff != -1:
#          print(desc)
          desc=desc[0:cutoff]
          nch = ud.lookup(desc)
#          print(desc)

      desc = ud.name(nch)
      if not nch in res:
        res[nch]=data[ch]
      else:
        res[nch]=sum(res[nch],data[ch])
    return res

def onlyLetters(data):
    res=dict()
    for ch in data:
      desc = ud.name(ch)
      grp = ud.category(ch)
      if grp[0]=='L':
        if grp[1]!='o':
          res[ch]=data[ch]
    return res

def onlyInAlphabet(data, alphabet):
    res=dict()
    for ch in data:
      if ch in alphabet:
        res[ch]=data[ch]
    return res

def removeSign(data):
    res=dict()
    for ch in data:
      desc = ud.name(ch)
      cutoff = desc.find(' SIGN')
      if cutoff == -1:
#        print('%s: %s' % (ch,desc))
        res[ch]=data[ch]
    return res

def recalculateRatio(data):
    res=dict()
    total=0
    for ch in data:
       total+=data[ch]['count']
    for ch in data:
       res[ch]=data[ch]
       res[ch]['ratio']=100*res[ch]['count']/total
#    print(total)
    return(res)
#      print('%s: %s' % (ch,desc))

def display(data, alphabet=None, fmt='%s: %2.2f%%'):
  fmt="|-\n| %s || {{st|%2.2f}}%%"
  if alphabet:
    for ch in alphabet:
      if ch in data:
        s=(fmt % (ch,data[ch]['ratio']))
        s=s.replace('.', ',')
        print(s)
  else:
    for ch in data:
        #desc = ud.name(ch)
#        print('%s: %s: %s: %d' % (ch,ud.category(ch), desc, data[ch]['count']))
        print(fmt % (ch,data[ch]['ratio']))

def toNoWiki(data, alphabet=None, fmt='%s: %2.2f%%'):
  fmt="|-\n| %s || {{st|%2.2f}}%%"
  if alphabet:
    for ch in alphabet:
      if ch in data:
        s=(fmt % (ch,data[ch]['ratio']))
        s=s.replace('.', ',')
        print(s)
  else:
    for ch in data:
        print(fmt % (ch,data[ch]['ratio']))

def main(src,dst):
  alphabet=[chr (i) for i in range(ord('a'), ord('z')+1)] + ['æ', 'ø', 'å']

  data=readCustom(src)
  #print(data)
  data=onlyLetters(data)
  #data=removeSign(data)
  #data=unsuper(data)
  data=lower(data)
  data=normalizeAlphabet(data, alphabet)
  data=onlyInAlphabet(data, alphabet)
  data=recalculateRatio(data)
  if not dst:
    toNoWiki(data, alphabet)
  else:
    writeCsv(dst,data, ['char', 'count', 'ratio'])
#  print(data)
#  print(alphabet)
  #writeCsv(dst,data, ['char', 'count', 'ratio'])

if __name__ == "__main__":
    if len(sys.argv)<1:
      sys.exit(1)
    src=sys.argv[1]
    dst=None
    if len(sys.argv)>2:
      dst=sys.argv[2]
    main(src,dst)
