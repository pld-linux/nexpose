# TODO
# - installer fails with error:
#   [Fail] - An unsupported version of Linux was detected: PLD 3.0
Summary:	Vulnerability Management Software
Name:		nexpose
Version:	4
Release:	0.1
License:	?
Group:		Applications/Networking
Source0:	http://download2.rapid7.com/download/NeXpose-v4/NeXposeSetup-Linux32.bin
# NoSource0-md5:	16e304a988dc07d41b5537de4706e623
NoSource:	0
Source1:	http://download2.rapid7.com/download/NeXpose-v4/NeXposeSetup-Linux64.bin
# NoSource1-md5:	6ef2b6d8e190744e60f58bc2428a426a
NoSource:	1
URL:		http://www.rapid7.com/products/nexpose/
BuildRequires:	fakeroot
BuildRequires:	jre >= 1.7
BuildRequires:	jre-X11 >= 1.7
BuildRequires:	sed >= 4.0
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Nexpose, proactively scans your environment for misconfigurations,
vulnerabilities, and malware and provides guidance for mitigating
risks.

Experience the power of Nexpose vulnerability management solutions by:
- Knowing the security risk of your entire IT environment including
  networks, operating systems, web applications and databases.
- Exposing security threats including vulnerabilities,
  misconfigurations and malware.
- Prioritizing threats and getting specific remediation guidance for
  each issue.
- Integrating with Metasploit to validate security risk in your
  environment.

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{SOURCE0}
%endif
%ifarch %{x8664}
SOURCE=%{SOURCE1}
%endif
%if %{without inst}
offset=$(grep -a 'tail -c' $SOURCE | awk '{print $3}')
size=$(stat -c %s $SOURCE)
tail -c $offset $SOURCE > sfx_archive.tar.gz
line=$(grep -an 'exit $returnCode' $SOURCE  | sed -rn '$s/^(.+):.+/\1/p')
head -n $line $SOURCE > sfx.sh
tar zxf sfx_archive.tar.gz
grep -aoE totalDataLength=[0-9]+ sfx.sh | cut -d= -f2 > totalDataLength.txt
%endif
ln -s $SOURCE src.sh
cat > installer.sh <<-'EOF'
classpath='i4jruntime.jar:user.jar:user/cryptojFIPS.jar:user/nsc.jar:user/nse.jar:user/nxshared.jar:user/r7shared.jar:user/sigar.jar:user/sslj.jar'
cwd=$(pwd)
module=$cwd/src.sh
%java \
	-Dinstall4j.jvmDir=%java_home \
	-Dexe4j.moduleName=$module \
	-Dexe4j.totalDataLength=$(cat totalDataLength.txt) \
	-Dinstall4j.cwd=$cwd \
	-Xmx128m \
	-Dsun.java2d.noddraw=true \
	-Di4j.vmov=true \
	-Di4j.vpt=true \
	-classpath $classpath \
	com.install4j.runtime.launcher.Launcher launch \
	com.install4j.runtime.installer.Installer \
	false false "" "" false true false "" true true 0 0 "" 20 20 "Arial" "0,0,0" 8 500 "version " 20 40 "Arial" "0,0,0" 8 500 -1 \
	"$@"
EOF

grep -Ev '^(#|$)' > cmds.txt <<-EOF
# Do you want to continue?
# Yes [y, Enter], No [n]
y

#Keep reading the license [1, Enter], Acknowledge having read the license [2], Cancel [3]
# Do you accept the license?
# 1. I accept the agreement. [1]
# 2. I do not accept the agreement. [2, Enter]
# 3. Cancel [3]
1
# ...
EOF

%install
rm -rf $RPM_BUILD_ROOT
fakeroot sh -x installer.sh -c < cmds.txt

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
