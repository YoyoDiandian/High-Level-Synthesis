LINK    = @echo linking $@ && g++ -w
GCC     = @echo compiling $@ && g++ -w
GC      = @echo compiling $@ && gcc -w
AR      = @echo generating static library $@ && ar crv
FLAGS   = -g -DDEBUG -W -Wall -fPIC
GCCFLAGS = 
DEFINES = 
HEADER  = -I./
LIBS    = 
LINKFLAGS =

#LIBS    += -lrt
#LIBS    += -pthread


hls: parser.o main.o
	$(LINK) $(FLAGS) $(LINKFLAGS) -o $@ $^ $(LIBS)

.cpp.o:
	$(GCC) -c $(HEADER) $(FLAGS) $(GCCFLAGS) -fpermissive -o $@ $<

.c.o:
	$(GC) -c $(HEADER) $(FLAGS) -fpermissive -o $@ $<

clean:
	rm -rf $(TARGET) *.o *.so *.a
	rm -rf hls
