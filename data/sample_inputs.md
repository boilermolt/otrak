# Sample Inputs

## workers.csv
```
worker_id,name,quals,normal_area
W001,Sam R.,basic_rp|class7_shipper,Turbine Hall
W002,Amy L.,basic_rp,Containment
```

## availability.csv
```
worker_id,available,preferred_shift,preferred_area,notes
W001,Y,10,Turbine Hall,Prefer 10s
W002,Y,Any,,
```

## work_orders.csv
```
work_order_id,title,area,critical_path,priority,shift_type,required_quals,headcount
WO-17,Pump overhaul,Bldg 2,Y,1,12,class7_shipper,1
WO-21,Decon support,Containment,N,3,10,basic_rp,3
```
