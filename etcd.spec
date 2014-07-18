%global debug_package %{nil}

Name:		etcd
Version:	0.4.5
Release:	1%{?dist}
Summary:	A highly-available key value store for shared configuration

License:	ASL 2.0
URL:		https://github.com/coreos/etcd/
Source0:	https://github.com/coreos/%{name}/archive/v%{version}/%{name}-v%{version}.tar.gz
Source1:	etcd.service
Source2:	etcd.socket
Patch0:         0001-De-bundle-third_party.patch

BuildRequires:	golang
BuildRequires:	golang(code.google.com/p/go.net)
BuildRequires:	golang(code.google.com/p/goprotobuf)
BuildRequires:	golang(github.com/BurntSushi/toml)
BuildRequires:	golang(bitbucket.org/kardianos/osext)
BuildRequires:	golang(github.com/coreos/go-log/log)
BuildRequires:	golang(github.com/coreos/go-systemd)
BuildRequires:	systemd

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
A highly-available key value store for shared configuration.

%prep
%setup -q -n %{name}-v%{version}
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
install -D -p -m 0755 etcd.bin %{buildroot}%{_bindir}/etcd
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.socket

%check
# empty for now

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%{_bindir}/etcd
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%doc LICENSE README.md Documentation/internal-protocol-versioning.md

%changelog
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
