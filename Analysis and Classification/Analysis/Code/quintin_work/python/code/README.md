#Python Code
<table>
<tr> <td><b>File Name</b></td> <td><b>Description</b></td> </tr>
<tr> <td>AddPacketId.py</td> <td><p>This script goes through all csv files in the current directory and appends a packet_id to each appliance gathering session. One packet_id represents one appliance reading. The csv files should be in the raw SEAD plug format from the data landing table in the original MySQL DB implementation.</p>  </td>
<tr> <td>consolidateRaw.py</td> <td>Gathers all metadata for raw csv files from MySQL database.</td> <tr>
<tr> <td><p>get_data.py </p> </td> <td>Utility to pull all consolidated content data from database in a clean nested format.</td> </tr>
<tr> <td>Classes.py</td> <td>Class file that acts as a utility file for AddPacketId.py script. Keep with AddPacketId.py at all times.</td> </tr>
<tr> <td>ClassesGetData.py</td> <td>Class representations to interact with database.</td> </tr>
</table>
