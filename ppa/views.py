from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape
from django.shortcuts import render_to_response
from models import SourcePackage
from debiantools import cowbuilder, parse_filename_deb, parse_filename_dsc
from os.path import basename

def ppa_packages(request):
    packages = SourcePackage.objects.all()
    return render_to_response('packages.html', {"packages": packages})

def ppa_upload(request):
    packages = SourcePackage.objects.all()
    from glob import glob
    newpackages = glob("/home/ondra/incoming/*.dsc")
    return render_to_response('upload.html', {"packages": packages,
        "newpackages": newpackages})

def ppa_buildlog(request, package_name):
    package = SourcePackage.objects.get(name__exact=package_name)
    log = package.build_log
    return render_to_response('error.html', {"text": 
        "<pre>"+log+"</pre>", "header":"Build log"})

def ppa_import(request):
    package_dsc = request.POST["package"]
    path, package_name, version = parse_filename_dsc(package_dsc)
    tar_gz = path+"/"+package_name+"_"+version+".tar.gz"
    if len(SourcePackage.objects.filter(name__exact=package_name)) != 0:
        return render_to_response('error.html', {"text": "The package with \
                the name <strong>%s</strong> already exists." % package_name})
    p = SourcePackage(name=package_name)
    from os import system
    archive = "/home/ondra/debian/unstable/"
    system("cp %s %s" % (package_dsc, archive))
    p.file_dsc = archive+basename(package_dsc)
    system("cp %s %s" % (tar_gz, archive))
    p.file_tar_gz = archive+basename(tar_gz)
    p.version = version
    p.status = "unbuilt"
    p.save()
    return HttpResponseRedirect("/ppa/packages/")

def ppa_delete(request):
    package_id = request.POST["package"]
    p = SourcePackage.objects.get(id=package_id)
    binary_packages = p.binarypackage_set.all()
    from os import system
    system("rm %s" % (p.file_dsc))
    system("rm %s" % (p.file_tar_gz))
    for bin in binary_packages:
        system("rm %s" % (bin.file_deb))
    p.delete()
    update_sources_list()
    return HttpResponseRedirect("/ppa/packages/")

def package_built(c):
    p = SourcePackage.objects.get(id=c.package_id)
    p.build_log = c.log
    p.status = "built"
    from os import system
    archive = "/home/ondra/debian/unstable/"
    for oldpath in c.packages:
        dir,pname,version,arch = parse_filename_deb(oldpath)
        system("mv %s %s" % (oldpath, archive))
        newpath = archive+pname+"_"+version+"_"+arch+".deb" 
        p.binarypackage_set.create(name=pname, file_deb=newpath, arch=arch)
    p.save()
    update_sources_list()

def ppa_build(request):
    package_id = request.POST["package"]
    p = SourcePackage.objects.get(id=package_id)
    c = cowbuilder(p.file_dsc, callback=package_built)
    c.package_id = package_id
    c.start()
    p.status = "building"
    p.save()
    return HttpResponseRedirect("/ppa/sourcepackage/%s" % p)

def ppa_sourcepackage(request, package_name):
    try:
        package = SourcePackage.objects.get(name__exact=package_name)
        binary_packages = package.binarypackage_set.all()
    #except AssertionError:
    #    package = SourcePackage.objects.filter(name__exact=package_name)[0]
    #    binary_packages = package.binarypackage_set.all()
    except SourcePackage.DoesNotExist:
        package = None
        binary_packages = None
    return render_to_response('sourcepackage.html', 
            {"package": package, "binary_packages": binary_packages})

def ppa_temp(request):
    import datetime
    now = datetime.datetime.now()
    mytable = [
            ["openmx", "building", "unstable"],
            ["petsc", "built", "gutsy"],
            ["petsc-2", "built", "gutsy"],
            ["petsc-3", "building", "gutsy"],
            ["petsc-3", "building", "unstable"],
            ]
    myheader = ["package", "state", "distribution"]
    return render_to_response('temp.html', {'current_date': now,
        "mytable": mytable, "myheader": myheader})

def ppa_contact(request):
    return render_to_response('contact.html', {})

def hello_text(request):
    "This view is a basic 'hello world' example in plain text."
    return HttpResponse('Hello, world.', mimetype='text/plain')

def hello_write(request):
    "This view demonstrates how an HttpResponse object has a write() method."
    r = HttpResponse()
    r.write("<p>Here's a paragraph.</p>")
    r.write("<p>Here's another paragraph.</p>")
    return r

def metadata(request):
    "This view demonstrates how to retrieve request metadata, such as HTTP headers."
    r = HttpResponse('<h1>All about you</h1>')
    r.write("<p>Here's all known metadata about your request, according to <code>request.META</code>:</p>")
    r.write('<table>')
    meta_items = request.META.items()
    meta_items.sort()
    for k, v in meta_items:
        r.write('<tr><th>%s</th><td>%r</td></tr>' % (k, v))
    r.write('</table>')
    return r

def get_data(request):
    "This view demonstrates how to retrieve GET data."
    r = HttpResponse()
    if request.GET:
        r.write('<p>GET data found! Here it is:</p>')
        r.write('<ul>%s</ul>' % ''.join(['<li><strong>%s:</strong> %r</li>' % (escape(k), escape(v)) for k, v in request.GET.items()]))
    r.write('<form action="" method="get">')
    r.write('<p>First name: <input type="text" name="first_name"></p>')
    r.write('<p>Last name: <input type="text" name="last_name"></p>')
    r.write('<p><input type="submit" value="Submit"></p>')
    r.write('</form>')
    return r

def post_data(request):
    "This view demonstrates how to retrieve POST data."
    r = HttpResponse()
    if request.POST:
        r.write('<p>POST data found! Here it is:</p>')
        r.write('<ul>%s</ul>' % ''.join(['<li><strong>%s:</strong> %r</li>' % (escape(k), escape(v)) for k, v in request.POST.items()]))
    r.write('<form action="" method="post">')
    r.write('<p>First name: <input type="text" name="first_name"></p>')
    r.write('<p>Last name: <input type="text" name="last_name"></p>')
    r.write('<p><input type="submit" value="Submit"></p>')
    r.write('</form>')
    return r

def update_sources_list():
    from pexpect import run
    from os import system
    system("cd /home/ondra/debian; dpkg-scanpackages unstable /dev/null > /tmp/Packages")
    print run("gzip /tmp/Packages")
    print run("rm -rf /home/ondra/debian/dists/")
    print run("mkdir -p /home/ondra/debian/dists/unstable/main/binary-i386/")
    print run("mv /tmp/Packages.gz /home/ondra/debian/dists/unstable/main/binary-i386/")

def ppa_sourceslist(request):
    update_sources_list()
    return HttpResponseRedirect("/ppa/packages/")
