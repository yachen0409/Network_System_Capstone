CC = g++
CFLAGS = -Wall
LIBS = -lpcap

SRCS = nscap_hw1.cpp
OBJS = $(SRCS:.cpp=.o)

.PHONY: all clean

all: main

main: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

%.o: %.cpp
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) main

.DEFAULT_GOAL := all

MAKEFLAGS += -B

