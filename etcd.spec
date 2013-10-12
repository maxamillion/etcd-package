%global debug_package %{nil}

Name:		etcd
Version:	0.1.2
Release:	3%{?dist}
Summary:	A highly-available key value store for shared configuration

License:	ASL 2.0
URL:		https://github.com/coreos/etcd/
Source0:	https://github.com/coreos/%{name}/archive/v%{version}/%{name}-v%{version}.tar.gz
Source1:	etcd.service
Source2:	etcd.socket
Patch1:		etcd-0001-feat-activation-add-socket-activation.patch

BuildRequires:	golang
BuildRequires:	systemd

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
A highly-available key value store for shared configuration.

%prep
%setup -q
echo "package main
const releaseVersion = \"%{version}\"" > release_version.go
%patch1 -p1 -b .systemd-activation
# These all packages should be unbundled
mkdir -p src/code.google.com/p
cp -r third_party/code.google.com/p/go.net/ src/code.google.com/p/
cp -r third_party/code.google.com/p/goprotobuf/ src/code.google.com/p/
mkdir -p src/github.com/coreos
cp -r third_party/github.com/coreos/go-log/ src/github.com/coreos/
cp -r third_party/github.com/coreos/go-raft/ src/github.com/coreos/
cp -r third_party/github.com/coreos/go-systemd/ src/github.com/coreos/
# for etcd itself
ln -s ../../../ src/github.com/coreos/etcd
mkdir -p src/bitbucket.org/kardianos
cp -r third_party/bitbucket.org/kardianos/osext/ src/bitbucket.org/kardianos/

%build
GOPATH="${PWD}" go build -v -x -o etcd

%install
install -D -p -m 0755 etcd %{buildroot}%{_bindir}/etcd
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
