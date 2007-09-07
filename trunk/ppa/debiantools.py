from threading import Thread

def parse_filename_dsc(file_dsc):
    """
    Parses "/path/to/tmobile-scripts_0.1.dsc" and returns
    ("/path/to",tmobile-scripts","0.1")
    """
    from os.path import dirname, basename
    dir = dirname(file_dsc)
    file = basename(file_dsc)
    file = file[:file.find("_")]
    version = file_dsc[file_dsc.find("_")+1:-4]
    #check that we decomposed the filename correctly
    assert dir+"/"+file+"_"+version+".dsc" == file_dsc
    return dir, file, version

def parse_filename_deb(file_deb):
    """
    Parses "/path/to/tmobile-scripts_0.1_i386.deb" and returns
    ("/path/to",tmobile-scripts","0.1","i386")
    """
    from os.path import dirname, basename
    dir = dirname(file_deb)
    base = basename(file_deb)
    file = base[:base.find("_")]
    base = file_deb[file_deb.find("_")+1:-4]
    version = base[:base.find("_")]
    arch = base[base.find("_")+1:]
    #check that we decomposed the filename correctly
    assert dir+"/"+file+"_"+version+"_"+arch+".deb" == file_deb
    return dir, file, version, arch

def execute(command):
    """Runs the "command", returns all output. Needs to be very robust."""
    import pexpect
    #log = pexpect.run(command)
    pexpect.run('bash -c "%s &> /tmp/log"' % command)
    log = "".join(open("/tmp/log").readlines())
    return log

class cowbuilder(Thread):
    """
    Builds a package in a new thread.

    Usage:

    c = cowbuilder("/path/to/tmobile-scripts_0.1.dsc")
    c.start()
    c.join() #or do whatever else
    assert not c.isAlive()
    print c.log
    """

    def __init__(self,package_dsc, output_dir=None, callback=None):
        Thread.__init__(self)
        self.package_dsc = package_dsc
        if output_dir == None:
            #default output dir is the same dir where *.dsc is
            from os.path import dirname
            self.output_dir = dirname(package_dsc)
        else:
            self.output_dir = output_dir

        self.callback = callback

    def run(self):
        from glob import glob
        execute("rm -rf /tmp/s")
        execute("mkdir /tmp/s")
        self.output_dir = "/tmp/s"
        command = "sudo cowbuilder --build %s --buildresult %s" % \
            ( self.package_dsc, self.output_dir )
        log = "$ "+command+"\n"
        print "There is going to be an exception now, don't know why..."
        log += execute(command)
        print "the exception should be above ^^^"
        self.log = log
        self.packages = glob("/tmp/s/*.deb")
        if self.callback:
            self.callback(self)
