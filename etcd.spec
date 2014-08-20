%global debug_package %{nil}
%global import_path     github.com/coreos/etcd
%global gopath          %{_datadir}/gocode

Name:		etcd
Version:	0.4.6
Release:	4%{?dist}
Summary:	A highly-available key value store for shared configuration

License:	ASL 2.0
URL:		https://github.com/coreos/etcd/
Source0:	https://github.com/coreos/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:	etcd.service
Source2:	etcd.conf
Patch0:         etcd-0.4.6-debundle-third_party-imports.patch

BuildRequires:	golang
BuildRequires:	golang(code.google.com/p/go.net)
BuildRequires:	golang(code.google.com/p/gogoprotobuf)
BuildRequires:	golang(github.com/BurntSushi/toml)
BuildRequires:	golang(github.com/gorilla/mux)
BuildRequires:	golang(github.com/mreiferson/go-httpclient)
BuildRequires:	golang(bitbucket.org/kardianos/osext)
BuildRequires:	golang(github.com/coreos/go-log/log)
BuildRequires:  golang(github.com/coreos/go-etcd/etcd)
BuildRequires:	golang(github.com/coreos/go-systemd)
BuildRequires:	golang(github.com/rcrowley/go-metrics)
BuildRequires:	systemd

Requires(pre):	shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
A highly-available key value store for shared configuration.

%package devel
BuildRequires:  golang
BuildRequires:  golang(code.google.com/p/go.net)
BuildRequires:  golang(code.google.com/p/gogoprotobuf)
BuildRequires:  golang(github.com/BurntSushi/toml)
BuildRequires:  golang(github.com/gorilla/mux)
BuildRequires:  golang(github.com/mreiferson/go-httpclient)
BuildRequires:  golang(bitbucket.org/kardianos/osext)
BuildRequires:  golang(github.com/coreos/go-log/log)
BuildRequires:  golang(github.com/coreos/go-systemd)
BuildRequires:  golang(github.com/rcrowley/go-metrics)
Requires:       golang
Summary:        etcd golang devel libraries
Provides:       golang(%{import_path}) = %{version}-%{release}

%description devel
golang development libraries for etcd, a highly-available key value store for
shared configuration.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
echo "package main
const releaseVersion = \"%{version}\"" > release_version.go

# etcd has its own fork of the client API
mkdir tmp
# And a raft fork: https://bugzilla.redhat.com/show_bug.cgi?id=1047194#c12
mv third_party/github.com/goraft tmp

# Nuke everything else though
rm -rf third_party

# And restore the third party bits we're keeping
mkdir -p third_party/github.com/coreos/
mv tmp/goraft third_party/github.com/
rmdir tmp

# Make link for etcd itself
mkdir -p src/github.com/coreos
ln -s ../../../ src/github.com/coreos/etcd

%build
GOPATH="${PWD}:%{_datadir}/gocode" go build -v -x -o etcd.bin

%install
install -d -m 0755 %{buildroot}%{_sysconfdir}/etcd
install -m 644 -t %{buildroot}%{_sysconfdir}/etcd %{SOURCE2}
install -D -p -m 0755 etcd.bin %{buildroot}%{_bindir}/etcd
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

# And create /var/lib/etcd
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/etcd

# Install files for devel sub-package
install -d %{buildroot}/%{gopath}/src/%{import_path}
cp -av main.go %{buildroot}/%{gopath}/src/%{import_path}/
cp -av go_version.go %{buildroot}/%{gopath}/src/%{import_path}/
for dir in bench config discovery Documentation error etcd fixtures http log \
           metrics mod pkg server store tests
do
    cp -av ${dir} %{buildroot}/%{gopath}/src/%{import_path}/
done

%check
# empty for now

%pre
getent group etcd >/dev/null || groupadd -r etcd
getent passwd etcd >/dev/null || useradd -r -g etcd -d %{_localstatedir}/lib/etcd \
	-s /sbin/nologin -c "etcd user" etcd
%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%config(noreplace) %{_sysconfdir}/etcd
%{_bindir}/etcd
%dir %attr(-,etcd,etcd) %{_localstatedir}/lib/etcd
%{_unitdir}/%{name}.service
%doc LICENSE README.md Documentation/internal-protocol-versioning.md

%files devel
%doc LICENSE README.md Documentation/internal-protocol-versioning.md
%dir %attr(755,root,root) %{gopath}/src/github.com/coreos
%dir %attr(755,root,root) %{gopath}/src/%{import_path}
%{gopath}/src/%{import_path}/*

%changelog
* Wed Aug 20 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.4.6-4
- Add BuildRequires for new go-etcd golang package, remove bundled version.

* Tue Aug 19 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.4.6-3
- Add devel sub-package

* Wed Aug 13 2014 Eric Paris <eparis@redhat.com> - 0.4.6-2
- Bump to 0.4.6
- run as etcd, not root

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Oct 20 2013 Peter Lemenkov <lemenkov@gmail.com> - 0.1.2-5
- goprotobuf library unbundled (see rhbz #1018477)
- go-log library unbundled (see rhbz #1018478)
- go-raft library unbundled (see rhbz #1018479)
- go-systemd library unbundled (see rhbz #1018480)
- kardianos library unbundled (see rhbz #1018481)

* Sun Oct 13 2013 Peter Lemenkov <lemenkov@gmail.com> - 0.1.2-4
- go.net library unbundled (see rhbz #1018476)

* Sat Oct 12 2013 Peter Lemenkov <lemenkov@gmail.com> - 0.1.2-3
- Prepare for packages unbundling
- Verbose build

* Sat Oct 12 2013 Peter Lemenkov <lemenkov@gmail.com> - 0.1.2-2
- Fix typo in the etc.service file

* Sat Oct 12 2013 Peter Lemenkov <lemenkov@gmail.com> - 0.1.2-1
- Ver. 0.1.2
- Integrate with systemd

* Mon Aug 26 2013 Luke Cypret <cypret@fedoraproject.org> - 0.1.1-1
- Initial creation
