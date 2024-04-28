#%% 
from dataclasses import dataclass
import numpy as np
from math import pow

## -------------------------------- definitions of types  ---------------------------------- //
@dataclass
class pointdata:
    prev:int #emulate double-linked list
    next: int 
    pvdiff: float #difference to previous
    
@dataclass
class pvtemppoint:
    it: int
    ev: float 

class pMetric(object):
	# temporary data used by Merge2GoodInt. Declaring it here avoids allocating/deallocating it at each call of Merge2GoodInt.
	av_mins:list[pvtemppoint]
	av_maxs:list[pvtemppoint]
	vb_mins:list[pvtemppoint]
	vb_maxs:list[pvtemppoint]
	links:list[pointdata] ## emulates double linked list in c++
	#links:DoublyLinkedList # type: ignore
	p:float
	
	## the difference used in p-variation, i.e. the abs power of diff.
	@staticmethod
	def pvar_diff(diff: float, p: float)->float:
		return pow(abs(diff), p)

	## please note that arg1, arg3 is supposed to be a const but this isn't respected in python
	@staticmethod
	def DetectLocalExtrema(x: list, links: list[pointdata], p: float)->None: # type: ignore
	# find local extrema and put them in a doubly linked list
		last_extremum: int
		direction = 0
		new_extremum = False
		n = len(x)
		cur_value = x[0]
		last_value = cur_value
		next_value: float
		last_link = pointdata(pvdiff=0,prev=0)
		
		for i in range(n):
			j = i + 1
			if (j != n):
				next_value = x[j]
				if (next_value>cur_value):
					new_extremum = (direction == -1)
					direction = 1
				elif(next_value<cur_value):
					new_extremum = (direction==1)
					direction = -1
				else:
					new_extremum = False
			
			else: 
				# last point is extremal
				new_extremum = True
			
			if (new_extremum):
				last_link.next = i
				links[last_extremum] = last_link
				last_link.prev = last_extremum
				last_link.pvdiff = pMetric.pvar_diff(cur_value - last_value, p)
				last_extremum = i
				last_value = cur_value
			
			cur_value = next_value
		last_link.next = n
		links.append(last_link)


	# Make sure that all intervals of length 3 are optimal
	@staticmethod
	def CheckShortIntervals(x: list, links: list[pointdata], p: float)->None:
	# Main principle:
	# if |pt[i] - pt[i+ d]|^p > sum_{j={i+1}}^d   |pt[j] - pt[j-1]|^p
	# but all shorter intervals are optimal,
	# then all middle points (i.e. p[j], j=i+1,...,i+d-1) are redundant

		csum = 0
		fjoinval : float
		pMetric.p = p

		int_begin = 0
		int_end = 0
		n = len(x)
		for i in range(3):
			int_end = links[int_end].next
			if (int_end == n):
				return # no intervals of this length
			csum += links[int_end].pvdiff

		loop_check = True
		while loop_check:
			fjoinval = pMetric.pvar_diff(x[int_begin] - x[int_end], p)
			if (csum >= fjoinval): #mid points are significant, continue to next interval
				int_end = links[int_end].next
				if (int_end == n):
					return #no next interval
				int_begin = links[int_begin].next
				csum -= links[int_begin].pvdiff
				csum += links[int_end].pvdiff
			else: # mid points are redundant, erase them
				links[int_begin].next = int_end
				links[int_end].prev = int_begin
				links[int_end].pvdiff = fjoinval
				# backtrack, because we don't know if the changed intervals are significant
				csum = fjoinval
				for i in range(1,3):
					if (int_begin >  0):
						csum += links[int_begin].pvdiff
						int_begin = links[int_begin].prev
					else:
						int_end = links[int_end].next
						if (int_end == n):
							return # no next interval
						csum += links[int_end].pvdiff


	# merge two intervals ([a, v] and [v, b]) which are known to be good.
	# Captures temporary variables by reference to avoid multiple allocation
	def Merge2GoodInt(x: list, a: int, v: int, b: int):
		# Main principle:
		# 1. Find potential points in intervals [a,v) and (v, b]
		#    (i.e. the points that could make a new f-joint with any point form opposite interval).
		#    Those points are find using cummin and cummac starting from v.
		#     Some points might be dropped out before actual checking, but experiment showed, that it is not worthwhile.
		# 2. Sequentially check all possible joints. If any increase is detected, then all middle points are insignificant.

		if (a==v or v==b): return # nothing to calculate, exit the procedure.

		amin:float
		amax:float
		bmin:float
		bmax:float
		ev:float
		balance:float
		maxbalance:float
		fjoin:float
		takefjoin:float
		#####
		# iterators for our doubly linked list
		ait = 0
		bit = 0
		tait = 0
		tbit = 0 
		sbit = 0
		#####
		prt_it:int
		pvtp:int

		#1. ### Find potential points
		pMetric.av_mins.clear()
		pMetric.av_maxs.clear()
		pMetric.vb_mins.clear()
		pMetric.vb_maxs.clear()

		# --- in interval [a,v) (starting from v).
		ev = 0
		prt_it = v
		amin = amax = x[v]
		while(prt_it!=a):
			ev += pMetric.links[prt_it].pvdiff
			prt_it = pMetric.links[prt_it].prev
			if(x[prt_it]>amax):
				amax=x[prt_it]
				pvtp.it = prt_it
				pvtp.ev = ev
				pMetric.av_maxs.append(pvtp)
			elif(x[prt_it]<amin):
				amin = x[prt_it]
				pvtp.it = prt_it
				pvtp.ev = ev
				pMetric.av_mins.append(pvtp)

		# --- in interval (v,b] (starting from v).
		ev = 0
		prt_it = v
		bmin = bmax = x[v]
		while(prt_it!=b):
			prt_it = pMetric.links[prt_it].next
			ev += pMetric.links[prt_it].pvdiff
			if(x[prt_it]>bmax):
				bmax = x[prt_it]
				pvtp.it = prt_it
				pvtp.ev = ev
				pMetric.vb_maxs.append(pvtp)
			elif( x[prt_it]<bmin):
				bmin = x[prt_it]
				pvtp.it = prt_it
				pvtp.ev = ev
				pMetric.vb_mins.append(pvtp)

		# 2. ### Sequentially check all possible joints: finding the best i,j \in [a, v)x(v,b] that could be joined
		takefjoin = 0
		maxbalance = 0
		maxFromA = True ## if max is from A then TRUE, if max is from B then FALSE
		sbit = 0 #pMetric.vb_maxs[0]
		while ait < len(pMetric.av_mins):
			bit = sbit
			while(bit != len(pMetric.vb_maxs)):
				fjoin = pMetric.pvar_diff(x[pMetric.av_mins[ait].it] - x[pMetric.vb_maxs[bit].it], pMetric.p)
				balance = fjoin - x[pMetric.vb_maxs[bit].it].ev - x[pMetric.av_mins[ait].it].ev
				if (balance>maxbalance):
					maxbalance = balance
					takefjoin = fjoin
					tait = ait
					sbit = tbit = bit
					maxFromA = False
				bit += 1
			ait += 1

		sbit = 0 #pMetric.vb_mins[0]
		ait = 0
		while(ait < len(pMetric.av_maxs)):
			bit = sbit
			while(bit!=len(pMetric.vb_mins)):
				fjoin = pMetric.pvar_diff( x[pMetric.av_maxs[ait].it] - x[pMetric.vb_mins[bit].it], pMetric.p)
				balance = fjoin - pMetric.vb_mins[bit].ev - pMetric.av_maxs[ait].ev
				if (balance>maxbalance):
					maxbalance = balance
					takefjoin = fjoin
					tait = ait
					sbit = tbit = bit
					maxFromA = True
				bit += 1
			ait += 1

		# if we found any point, join it by erasing all middle points
		if(maxbalance>0):
			pMetric.links[pMetric.av_maxs[tait].it if maxFromA else pMetric.av_mins[tait].it].next = \
				pMetric.vb_mins[tbit].it if maxFromA else pMetric.vb_maxs[tbit].it
			pMetric.links[pMetric.vb_mins[tbit].it if maxFromA else pMetric.vb_maxs[tbit].it].prev = \
				(pMetric.av_maxs[tait].it if maxFromA else pMetric.av_mins[tait].it).next
			pMetric.links[pMetric.vb_mins[tbit].it if maxFromA else pMetric.vb_maxs[tbit].it].pvdiff = takefjoin
			 

	# Merge optimal intervals. LSI is the length of optimal intervals in the beginning.
	def MergeIntervalsRecursively(x: list, links: list[pointdata], p: int, LSI: int =2)->None:

		# Main principle:
		# 1. Put endpoints of optimal intervals in IterList
		# 2. Merge pairs of adjacent intervals using the function Merge2GoodInt. Repeat until all intervals are merged.


		it = 0
		IterList:list[int]
		# stores iterators for list
		a_IL = 0
		v_IL = 0
		b_IL = 0

		### 1. Finding all the intervals that will be merged
		count = 0
		while(it < len(x)):
			if(count % LSI == 0):
				IterList.append(it)
			count += 1
			it = pMetric.links[it].next
		IterList.append(len(x)-1)

		### 2. Merging pairs of interval until everything is merged.
		# std::list<T>::size has constant complexity since C++11
		while(len(IterList)>2):
			a_IL = IterList.begin()
			while (len(IterList) > 0):
				# we are guaranteed that a_IL != IterList.end() here
				v_IL = a_IL
				v_IL += 1
				if (v_IL != IterList.end()):
					b_IL = v_IL
					b_IL += 1
					if (b_IL != IterList.end()):
						pMetric.Merge2GoodInt(links[a_IL], links[v_IL], links[b_IL])
						a_IL = IterList.erase(v_IL) # now a_IL == b_IL
					else:
						break
				else:
					break
				

	# p-variation calculation (in Python)
	def pvar(x:list, p:float)-> float: # type: ignore

		# short special cases
		if (len(x) <= 2):
			if (len(x) <= 1):
				return 0
			else:
				return pow(abs(x[0]-x[1]), p)

		pMetric.links.clear()

		pMetric.DetectLocalExtrema(x, pMetric.links,  p)
		pMetric.CheckShortIntervals(x, pMetric.links, p)
		pMetric.MergeIntervalsRecursively(x, pMetric.links, p, 4)

		# output:
		pvalue=0
		i = 0
		while ( i < len(x) ):
			pvalue += pMetric.links[i].pvdiff
			i = pMetric.links[i].next

		return pvalue