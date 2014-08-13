%global debug_package %{nil}

Name:		etcd
Version:	0.4.6
Release:	2%{?dist}
Summary:	A highly-available key value store for shared configuration

License:	ASL 2.0
URL:		https://github.com/coreos/etcd/
Source0:	https://github.com/coreos/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:	etcd.service
Source2:	etcd.conf
Patch0:         0001-De-bundle-third_party.patch

BuildRequires:	golang
BuildRequires:	golang(code.google.com/p/go.net)
BuildRequires:	golang(code.google.com/p/gogoprotobuf)
BuildRequires:	golang(github.com/BurntSushi/toml)
BuildRequires:	golang(github.com/gorilla/mux)
BuildRequires:	golang(github.com/mreiferson/go-httpclient)
BuildRequires:	golang(bitbucket.org/kardianos/osext)
BuildRequires:	golang(github.com/coreos/go-log/log)
BuildRequires:	golang(github.com/coreos/go-systemd)
BuildRequires:	golang(github.com/rcrowley/go-metrics)
BuildRequires:	systemd

Requires(pre):	shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
A highly-available key value store for shared configuration.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
echo "package main
const releaseVersion = \"%{version}\"" > release_version.go

# etcd has its own fork of the client API
mkdir tmp
mv third_party/github.com/coreos/go-etcd tmp
# And a raft fork: https://bugzilla.redhat.com/show_bug.cgi?id=1047194#c12
mv third_party/github.com/goraft tmp

# Nuke everything else though
rm -rf third_party

# And restore the third party bits we're keeping
mkdir -p third_party/github.com/coreos/
mv tmp/go-etcd third_party/github.com/coreos/
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

%changelog
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
