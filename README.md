
# Batin
<p>Batin maps byte addresses to the line numbers of the corresponding source code.</p>
<p>Why Batin exists?</p>
<p>Some existing security analysis tools of Ethereum smart contracts report vulnerabilities at the byte addresses.
The published benchmarks label vulnerabilities with line numbers at the source code level. To assist the vulnerability analysis, this tool is designed to identify the line numbers of the souce code for the  byte addresses.</p>


How to run Batin:<br>
```bash
$ map analyze <solidity file path>:<contract name>
```
<p>&nbsp;&nbsp;</p>
<hr>
