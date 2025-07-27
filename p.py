nums=[1,2,3,4]
n=len(nums)
output=[]
for i in range(n-1):
    product=nums[i]
    for j in range(i+1,n):
        product*=nums[j]
        print(product)
        if product not in nums:
            output.append(product)
print(output)
