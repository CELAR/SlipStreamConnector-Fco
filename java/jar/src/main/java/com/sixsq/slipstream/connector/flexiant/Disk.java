package com.sixsq.slipstream.connector.flexiant;

import java.util.ArrayList;
import java.util.List;


public class Disk {
	
	static List<String> disks = new ArrayList<String>();
	
	public static List<String> getList(){
		if (disks.size() == 0){
			disks.add("20");
			disks.add("50");
			disks.add("100");
		}
		return disks;
	}
	
}
