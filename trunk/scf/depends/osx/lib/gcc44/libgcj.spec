#
# This spec file is read by gcj when linking.
# It is used to specify the standard libraries we need in order
# to link with libgcj.
#
%rename startfile startfileorig
*startfile:  %(startfileorig)

%rename lib liborig
*lib:  %{s-bc-abi:} -lgcj  -lm -liconv  -lpthread -lz -allow_stack_execute  -ldl %(libgcc)  %(liborig)

*jc1: -fhash-synchronization -fuse-divide-subroutine -fcheck-references -fuse-boehm-gc -fnon-call-exceptions   -fkeep-inline-functions
