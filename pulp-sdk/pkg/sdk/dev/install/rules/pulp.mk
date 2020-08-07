PULP_LDFLAGS += -lbench
override CONFIG_OPT += rt/start-all=true

#override PULP_PROPERTIES += soc/fc soc/cluster
#
#ifeq '$(soc/fc)' ''
#cluster=1
#endif
#
#ifeq '$(soc/cluster)' ''
#fc=1
#endif
#

ifndef cluster
fc=1
endif

include $(PULP_SDK_INSTALL)/rules/pulp_rt.mk
